from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse, NoReverseMatch
import json

from django_adelaidex.test import UserSetUp
from votes.models import Vote
from submissions.models import Submission
from exhibitions.models import Exhibition
from artwork.models import Artwork

class VoteTests(UserSetUp, TestCase):
    def setUp(self):
        super(VoteTests, self).setUp()
        self.exhibition = Exhibition.objects.create(title='New Exhibition', description='description goes here', author=self.user)
        self.artwork = Artwork.objects.create(title='New Artwork', code='// code goes here', author=self.user)
        self.submission = Submission.objects.create(exhibition=self.exhibition, artwork=self.artwork, submitted_by=self.user)

class ShowVoteViewTests(VoteTests):

    """Vote view is JSON"""

    def test_view(self):
        vote = Vote.objects.create(submission=self.submission, status=Vote.THUMBS_UP, voted_by=self.user)
        client = Client()
        view_url = reverse('vote-view', kwargs={'pk': vote.id})

        # login required
        client.get(view_url)
        response = self.assertLogin(client, view_url)

        self.assertEqual('application/json', response.get('Content-Type'))
        parsed = json.loads(response.content)
        self.assertEquals(vote.id, parsed['id'])
        self.assertEquals('%s' % self.user, parsed['voted_by'])
        self.assertEquals('%s' % vote.submission, parsed['submission'])

    def test_view_not_found(self):
        client = Client()
        view_url = reverse('vote-view', kwargs={'pk': 100})
        client.get(view_url)
        response = self.assertLogin(client, view_url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual('text/html; charset=utf-8', response.get('Content-Type'))


class CreateVoteViewTests(VoteTests):

    '''Votes are created by liking a submission'''
    def create_vote_url(self, submission_id=None):
        if not submission_id:
            submission_id = self.submission.id
        return reverse('submission-like', kwargs={'submission': submission_id})

    def test_post_only(self):
        client = Client()
        create_url = self.create_vote_url()
        client.get(create_url)
        response = self.assertLogin(client, create_url)
        self.assertEqual(response.status_code, 403)

    def test_create(self):
        client = Client()
        self.assertLogin(client)

        # Can create a vote using the resolved url alone
        post_data = {}
        response = client.post(self.create_vote_url(), post_data)
        view_url = reverse('vote-view', kwargs={'pk': 1})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        response = client.get(view_url)
        self.assertEqual('application/json', response.get('Content-Type'))

        parsed = json.loads(response.content)
        self.assertEquals(1, parsed['id'])
        self.assertEquals('%s' % self.user, parsed['voted_by'])
        self.assertEquals('%s' % self.submission, parsed['submission'])

    def test_create_denied(self):
        client = Client()
        self.assertLogin(client)

        # Can vote once
        create_url = self.create_vote_url()
        view_url = reverse('vote-view', kwargs={'pk': self.submission.id})
        response = client.post(create_url)
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # But can't vote twice on the same submission
        response = client.post(create_url)
        self.assertEquals(response.status_code, 403)

        # Can vote on another submission, though
        artwork2 = Artwork.objects.create(title='Another Artwork', code='// code goes here', author=self.user)
        submission2 = Submission.objects.create(exhibition=self.exhibition, artwork=artwork2, submitted_by=self.user)
        create_url2 = self.create_vote_url(submission_id=submission2.id)
        view_url2 = reverse('vote-view', kwargs={'pk': submission2.id})
        response = client.post(create_url2)
        self.assertRedirects(response, view_url2, status_code=302, target_status_code=200)

    def test_create_invalid(self):
        client = Client()
        self.assertLogin(client)

        # Try to vote on a submission that doesn't exist
        bad_submission_url = self.create_vote_url(submission_id=100)
        response = client.post(bad_submission_url)
        self.assertEqual(response.status_code, 400)


class DeleteVoteViewTests(VoteTests):

    '''Votes are deleted by unliking a submission'''

    def setUp(self):
        super(DeleteVoteViewTests, self).setUp()

    def delete_vote_url(self, submission_id=None):
        if not submission_id:
            submission_id = self.submission.id
        return reverse('submission-unlike', kwargs={'submission': submission_id})

    def test_post_only(self):
        client = Client()
        delete_url = self.delete_vote_url()
        client.get(delete_url)
        response = self.assertLogin(client, delete_url)
        self.assertEquals(response.status_code, 403)

    def test_delete_own(self):
        client = Client()
        student_vote = Vote.objects.create(submission=self.submission, status=Vote.THUMBS_UP, voted_by=self.user)
        staff_vote = Vote.objects.create(submission=self.submission, status=Vote.THUMBS_UP, voted_by=self.staff_user)
        super_vote = Vote.objects.create(submission=self.submission, status=Vote.THUMBS_UP, voted_by=self.super_user)

        delete_url = self.delete_vote_url()
        ok_url = reverse('vote-ok')

        # Student can delete own votes
        self.assertLogin(client, user="student")
        view_url = reverse('vote-view', kwargs={'pk': student_vote.id})
        response = client.post(delete_url)
        self.assertRedirects(response, ok_url, status_code=302, target_status_code=200)
        response = client.get(view_url)
        self.assertEquals(response.status_code, 404)

        # Staff can delete own votes
        self.assertLogin(client, user='staff')
        view_url = reverse('vote-view', kwargs={'pk': staff_vote.id})
        response = client.post(delete_url)
        self.assertRedirects(response, ok_url, status_code=302, target_status_code=200)
        response = client.get(view_url)
        self.assertEquals(response.status_code, 404)

        # Superusers can delete own votes
        self.assertLogin(client, user='super')
        view_url = reverse('vote-view', kwargs={'pk': super_vote.id})
        response = client.post(delete_url)
        self.assertRedirects(response, ok_url, status_code=302, target_status_code=200)
        response = client.get(view_url)
        self.assertEquals(response.status_code, 404)

    def test_delete_not_found(self):
        client = Client()
        self.assertLogin(client)

        # Cannot delete a vote that does not exist
        delete_url = self.delete_vote_url()
        response = client.post(delete_url)
        self.assertEqual(response.status_code, 404)

    def test_delete_denied(self):
        client = Client()

        # Can delete a vote once
        vote = Vote.objects.create(submission=self.submission, status=Vote.THUMBS_UP, voted_by=self.user)
        ok_url = reverse('vote-ok')

        self.assertLogin(client)
        delete_url = self.delete_vote_url()
        response = client.post(delete_url)
        self.assertRedirects(response, ok_url, status_code=302, target_status_code=200)

        # But not twice
        response = client.post(delete_url)
        self.assertEquals(response.status_code, 404)
