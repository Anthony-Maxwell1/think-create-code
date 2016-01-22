from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.utils import timezone
from datetime import timedelta

from django_adelaidex.util.test import UserSetUp
from django_adelaidex.lti.models import Cohort
from submissions.models import Submission
from exhibitions.models import Exhibition
from artwork.models import Artwork
from votes.models import Vote

class SubmissionShowViewTests(UserSetUp, TestCase):

    def setUp(self):
        super(SubmissionShowViewTests, self).setUp()

        self.artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        self.exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = timezone.now(),
            author=self.user)

    def test_404(self):
        client = Client()
        view_url = reverse('submission-view', kwargs={'pk': 1})
        response = client.get(view_url)
        self.assertEqual(response.status_code, 404)
        
    def test_view(self):
        client = Client()
        submission = Submission.objects.create(
            artwork=self.artwork,
            exhibition=self.exhibition,
            submitted_by=self.user)

        view_url = reverse('submission-view', kwargs={'pk': submission.id})
        response = client.get(view_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('share_url' in response.context)
        self.assertEquals(response.context['votes'], {})
    
    def test_author_view(self):
        client = Client()
        submission = Submission.objects.create(
            artwork=self.artwork,
            exhibition=self.exhibition,
            submitted_by=self.user)

        logged_in = client.login(username=self.get_username(), password=self.get_password())
        self.assertTrue(logged_in)
        view_url = reverse('submission-view', kwargs={'pk': submission.id})
        response = client.get(view_url)
        self.assertEqual(response.status_code, 200)

        self.assertTrue('share_url' in response.context)
        self.assertEquals(response.context['votes'], {})
        self.assertEquals(response.context['submission'].score, 0)
    
    def test_votes_view(self):
        client = Client()
        submission = Submission.objects.create(
            artwork=self.artwork,
            exhibition=self.exhibition,
            submitted_by=self.user)
        vote = Vote.objects.create(submission=submission,
            status=Vote.THUMBS_UP, voted_by=self.user)

        # anonymous users don't see others' votes, just the score
        view_url = reverse('submission-view', kwargs={'pk': submission.id})
        response = client.get(view_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('share_url' in response.context)
        self.assertEquals(response.context['votes'], {})
        self.assertEquals(response.context['submission'].score, 1)

        # logged-in users see own votes
        logged_in = client.login(username=self.get_username(), password=self.get_password())
        self.assertTrue(logged_in)
        view_url = reverse('submission-view', kwargs={'pk': submission.id})
        response = client.get(view_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('share_url' in response.context)
        self.assertEquals(response.context['votes'], {submission.id: vote})
        self.assertEquals(response.context['submission'].score, 1)

        client.logout()
        logged_in = client.login(username=self.get_username('staff'), password=self.get_password('staff'))
        self.assertTrue(logged_in)
        view_url = reverse('submission-view', kwargs={'pk': submission.id})
        response = client.get(view_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('share_url' in response.context)
        self.assertEquals(response.context['votes'], {})
        self.assertEquals(response.context['submission'].score, 1)
    

class SubmissionCodeViewTests(UserSetUp, TestCase):
    """Submission view code tests."""

    def test_code_view(self):
        
        client = Client()

        # Submissions are shared and can be downloaded
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = timezone.now(),
            author=self.user)
        submission = Submission.objects.create(
            artwork=artwork,
            exhibition=exhibition,
            submitted_by=self.user)

        code_url = reverse('artwork-shared-code', kwargs={'pk':submission.id})
        response = client.get(code_url)
        self.assertEquals(response.get('Content-Disposition'), 'attachment;')
        self.assertEquals(response.context['object'].artwork, artwork)


class SubmissionListExhibitionViewTests(UserSetUp, TestCase):
    """Exhibition view includes Submission list."""

    def setUp(self):
        super(SubmissionListExhibitionViewTests, self).setUp()

        self.exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = timezone.now(),
            author=self.user)
        self.view_url = reverse('exhibition-view', kwargs={'pk': self.exhibition.id})

    def test_view(self):

        client = Client()

        # New exhibitions contain no submissions

        response = client.get(self.view_url)
        self.assertEquals(response.context['object'].id, self.exhibition.id)
        self.assertEquals(response.context['submissions']['object_list'].count(), 0)
        self.assertEquals(response.context['order'], 'recent')
        self.assertEquals(response.context['votes'], {})

        # Submit an artwork to the exhibition to see it in the list
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        submission = Submission.objects.create(artwork=artwork, exhibition=self.exhibition, submitted_by=self.user)

        response = client.get(self.view_url)
        self.assertEquals(response.context['object'].id, self.exhibition.id)
        submissions = response.context['submissions']['object_list'].all()
        self.assertEquals(submissions.count(), 1)
        self.assertEquals(submissions[0].id, submission.id)

    def test_sort_submissions(self):

        client = Client()

        # New exhibitions contain no submissions

        response = client.get(self.view_url)
        self.assertEquals(response.context['object'].id, self.exhibition.id)
        self.assertEquals(response.context['submissions']['object_list'].count(), 0)
        self.assertEquals(response.context['order'], 'recent')
        self.assertEquals(response.context['votes'], {})

        # Submit three artwork to the exhibition to see them in the list
        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        submission1 = Submission.objects.create(artwork=artwork1, exhibition=self.exhibition, submitted_by=self.user, score=10)

        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.user)
        submission2 = Submission.objects.create(artwork=artwork2, exhibition=self.exhibition, submitted_by=self.user, score=0)

        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.user)
        submission3 = Submission.objects.create(artwork=artwork3, exhibition=self.exhibition, submitted_by=self.user, score=5)

        response = client.get(self.view_url)
        self.assertEquals(response.context['object'].id, self.exhibition.id)
        submissions = response.context['submissions']['object_list']
        self.assertEquals(response.context['order'], 'recent')
        self.assertEquals(submissions.count(), 3)
        self.assertEquals(submissions[0].id, submission3.id)
        self.assertEquals(submissions[1].id, submission2.id)
        self.assertEquals(submissions[2].id, submission1.id)

        view_score_url = reverse('exhibition-view-score', kwargs={'pk': self.exhibition.id})
        response = client.get(view_score_url)
        self.assertEquals(response.context['object'].id, self.exhibition.id)
        submissions = response.context['submissions']['object_list']
        self.assertEquals(response.context['order'], 'score')
        self.assertEquals(submissions.count(), 3)
        self.assertEquals(submissions[0].id, submission1.id)
        self.assertEquals(submissions[1].id, submission3.id)
        self.assertEquals(submissions[2].id, submission2.id)

    def test_votes_public(self):
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        submission = Submission.objects.create(artwork=artwork, exhibition=self.exhibition, submitted_by=self.user)

        client = Client()

        # No votes, no vote text shown
        response = client.get(self.view_url)
        self.assertEquals(response.context['submissions']['object_list'].count(), 1)
        self.assertRegexpMatches(response.content, r'0 votes')
        self.assertRegexpMatches(response.content, r'Sign in to vote')

        # Add a vote, ensure it's shown correctly
        student_vote = Vote.objects.create(submission=submission, status=Vote.THUMBS_UP, voted_by=self.user)
        response = client.get(self.view_url)
        self.assertEquals(response.context['submissions']['object_list'].count(), 1)
        self.assertRegexpMatches(response.content, r'1 vote')
        self.assertRegexpMatches(response.content, r'Sign in to vote')

        # Add a second vote, ensure it's shown correctly
        staff_vote = Vote.objects.create(submission=submission, status=Vote.THUMBS_UP, voted_by=self.staff_user)
        response = client.get(self.view_url)
        self.assertEquals(response.context['submissions']['object_list'].count(), 1)
        self.assertRegexpMatches(response.content, r'2 votes')
        self.assertRegexpMatches(response.content, r'Sign in to vote')

    def test_vote_like(self):
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        submission = Submission.objects.create(artwork=artwork, exhibition=self.exhibition, submitted_by=self.user)

        client = Client()

        # Login as student
        response = self.assertLogin(client, self.view_url)
        self.assertEquals(response.context['submissions']['object_list'].count(), 1)
        self.assertNotRegexpMatches(response.content, r'title="unlike"')
        self.assertRegexpMatches(response.content, r'title="like"')

        # Add a vote, ensure it's shown correctly
        student_vote = Vote.objects.create(submission=submission, status=Vote.THUMBS_UP, voted_by=self.user)
        response = client.get(self.view_url)
        submissions = response.context['submissions']['object_list'].all()
        self.assertEquals(len(submissions), 1)
        self.assertEquals(submissions[0].score, 1)
        self.assertNotRegexpMatches(response.content, r'title="like"')
        self.assertRegexpMatches(response.content, r'title="unlike"')

        # Add a staff vote, ensure it doesn't affect the like/unlike button
        staff_vote = Vote.objects.create(submission=submission, status=Vote.THUMBS_UP, voted_by=self.staff_user)
        response = client.get(self.view_url)
        submissions = response.context['submissions']['object_list'].all()
        self.assertEquals(len(submissions), 1)
        self.assertEquals(submissions[0].score, 2)
        self.assertNotRegexpMatches(response.content, r'title="like"')
        self.assertRegexpMatches(response.content, r'title="unlike"')

    def test_artwork_shared_list(self):
        
        client = Client()
        list_path = reverse('artwork-shared')
        response = client.get(list_path)

        self.assertEquals(list(response.context['object_list']), [])

        artwork1p = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        submission1 = Submission.objects.create(artwork=artwork1, exhibition=self.exhibition, submitted_by=self.user)
        artwork2p = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        submission2 = Submission.objects.create(artwork=artwork2, exhibition=self.exhibition, submitted_by=self.user)
        artwork3p = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)
        submission3 = Submission.objects.create(artwork=artwork3, exhibition=self.exhibition, submitted_by=self.user)

        # Shared artwork is visible to public
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 3)
        self.assertEquals(response.context['object_list'][0], submission3)
        self.assertEquals(response.context['object_list'][1], submission2)
        self.assertEquals(response.context['object_list'][2], submission1)
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-shared-zip'))

        # Only shared artwork is visible to logged-in users in artwork-shared view
        response = self.assertLogin(client, list_path)
        self.assertEquals(response.context['object_list'].count(), 3)
        self.assertEquals(response.context['object_list'][0], submission3)
        self.assertEquals(response.context['object_list'][1], submission2)
        self.assertEquals(response.context['object_list'][2], submission1)
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-shared-zip'))

        response = self.assertLogin(client, list_path, user='staff')
        self.assertEquals(response.context['object_list'].count(), 3)
        self.assertEquals(response.context['object_list'][0], submission3)
        self.assertEquals(response.context['object_list'][1], submission2)
        self.assertEquals(response.context['object_list'][2], submission1)
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-shared-zip'))

        response = self.assertLogin(client, list_path, user='super')
        self.assertEquals(response.context['object_list'].count(), 3)
        self.assertEquals(response.context['object_list'][0], submission3)
        self.assertEquals(response.context['object_list'][1], submission2)
        self.assertEquals(response.context['object_list'][2], submission1)
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-shared-zip'))

    def test_artwork_shared_score_list(self):
        
        client = Client()
        list_path = reverse('artwork-shared-score')
        response = client.get(list_path)

        self.assertEquals(list(response.context['object_list']), [])

        artwork1p = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        submission1 = Submission.objects.create(artwork=artwork1, exhibition=self.exhibition, submitted_by=self.user, score=10)
        artwork2p = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        submission2 = Submission.objects.create(artwork=artwork2, exhibition=self.exhibition, submitted_by=self.user, score=5)
        artwork3p = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)
        submission3 = Submission.objects.create(artwork=artwork3, exhibition=self.exhibition, submitted_by=self.user, score=1)

        # Sort by highest score
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 3)
        self.assertEquals(response.context['object_list'][0], submission1)
        self.assertEquals(response.context['object_list'][1], submission2)
        self.assertEquals(response.context['object_list'][2], submission3)
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-shared-score-zip'))

        # Only shared artwork is visible to logged-in users in artwork-shared view
        response = self.assertLogin(client, list_path)
        self.assertEquals(response.context['object_list'].count(), 3)
        self.assertEquals(response.context['object_list'][0], submission1)
        self.assertEquals(response.context['object_list'][1], submission2)
        self.assertEquals(response.context['object_list'][2], submission3)
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-shared-score-zip'))

        response = self.assertLogin(client, list_path, user='staff')
        self.assertEquals(response.context['object_list'].count(), 3)
        self.assertEquals(response.context['object_list'][0], submission1)
        self.assertEquals(response.context['object_list'][1], submission2)
        self.assertEquals(response.context['object_list'][2], submission3)
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-shared-score-zip'))

        response = self.assertLogin(client, list_path, user='super')
        self.assertEquals(response.context['object_list'].count(), 3)
        self.assertEquals(response.context['object_list'][0], submission1)
        self.assertEquals(response.context['object_list'][1], submission2)
        self.assertEquals(response.context['object_list'][2], submission3)
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-shared-score-zip'))


class SubmissionCreateTests(UserSetUp, TestCase):

    def test_login(self):
        client = Client()

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        create_url = reverse('artwork-submit', kwargs={'artwork': artwork.id})
        client.get(create_url)
        self.assertLogin(client, create_url)

    def test_post_only(self):
        client = Client()

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        create_url = reverse('artwork-submit', kwargs={'artwork': artwork.id})
        client.get(create_url)
        response = self.assertLogin(client, create_url)
        self.assertEqual(response.status_code, 403)

    def test_no_choices(self):
        client = Client()

        create_url = reverse('artwork-submit', kwargs={'artwork': 1})
        self.assertLogin(client, create_url, user=self.staff_user)

        response = client.post(create_url, {})
        self.assertEquals(response.status_code, 200)
        self.assertRegexpMatches(response.content, r'Artwork:.*Sorry, no choices available')
        self.assertRegexpMatches(response.content, r'Exhibition:.*Sorry, no choices available')

    def test_submit_own_artwork(self):
        client = Client()

        student_artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        staff_artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.staff_user)
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = timezone.now(),
            author=self.user)

        create_url = reverse('artwork-submit', kwargs={'artwork': student_artwork.id})
        self.assertLogin(client, create_url)

        # Student can submit own artwork
        post_data = {
            'artwork': student_artwork.id,
            'exhibition': exhibition.id,
        }
        response = client.post(create_url, post_data)
        view_url = reverse('submission-view', kwargs={'pk':1})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure submission is in the exhibition view list
        response = client.get(reverse('exhibition-view', kwargs={'pk':exhibition.id}))
        self.assertEquals(response.context['object'].id, exhibition.id)
        submissions = response.context['submissions']['object_list'].all()
        self.assertEquals(submissions.count(), 1)
        self.assertEquals(submissions[0].id, student_artwork.id)

        # Student cannot submit others' artwork
        create_url = reverse('artwork-submit', kwargs={'artwork': staff_artwork.id})
        post_data = {
            'artwork': staff_artwork.id,
            'exhibition': exhibition.id,
        }
        response = client.post(create_url, post_data)
        self.assertEqual(response.status_code, 403)

        # Not by the student artwork submit URL either
        create_url = reverse('artwork-submit', kwargs={'artwork': student_artwork.id})
        post_data = {
            'artwork': staff_artwork.id,
            'exhibition': exhibition.id,
        }
        response = client.post(create_url, post_data)
        self.assertEqual(response.status_code, 403)

    def test_multiple_choices(self):
        client = Client()

        artwork = Artwork.objects.create(title='New Artwork', code='// code goes here', author=self.user)
        exhibition1 = Exhibition.objects.create(
            title='Exhibition One',
            description='description goes here',
            released_at = timezone.now(),
            author=self.user)

        exhibition2 = Exhibition.objects.create(
            title='Exhibition Two',
            description='description goes here',
            released_at = timezone.now(),
            author=self.user)

        create_url = reverse('artwork-submit', kwargs={'artwork': artwork.id})
        self.assertLogin(client, create_url)

        post_data = {
            'exhibition': exhibition1.id,
        }
        response = client.post(create_url, post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['form'].fields['exhibition'].queryset.all()), 2)

    def test_cohort_choices(self):
        client = Client()

        cohort1 = Cohort.objects.create(
            title='Cohort 1',
            oauth_key='abc',
            oauth_secret='abc',
            is_default=True,
        )
        cohort2 = Cohort.objects.create(
            title='Cohort 2',
            oauth_key='def',
            oauth_secret='def',
        )
        exhibition_no_cohort = Exhibition.objects.create(
            title='Exhibition No Cohort',
            description='description goes here',
            author=self.user)
        exhibition_cohort1 = Exhibition.objects.create(
            title='Exhibition Cohort1',
            description='description goes here',
            cohort=cohort1,
            author=self.user)
        exhibition_cohort2 = Exhibition.objects.create(
            title='Exhibition Cohort2',
            description='description goes here',
            cohort=cohort2,
            author=self.user)

        # User in no cohort
        artwork = Artwork.objects.create(title='New Artwork', code='// code goes here', author=self.user)
        create_url = reverse('artwork-submit', kwargs={'artwork': artwork.id})
        self.assertLogin(client, create_url)

        post_data = {
            'artwork': artwork.id,
        }
        response = client.post(create_url, post_data)
        self.assertEquals(response.status_code, 200)

        # Exhibition choices should be "no cohort" and the default
        exhibitions = response.context['form'].fields['exhibition'].queryset.all()
        self.assertEquals(len(exhibitions), 2)
        self.assertEquals(exhibitions[0], exhibition_no_cohort)
        self.assertEquals(exhibitions[1], exhibition_cohort1)

        # Move user into cohort1, no change to choices
        self.user.cohort = cohort1
        self.user.save()
        response = client.post(create_url, post_data)
        exhibitions = response.context['form'].fields['exhibition'].queryset.all()
        self.assertEquals(len(exhibitions), 2)
        self.assertEquals(exhibitions[0], exhibition_no_cohort)
        self.assertEquals(exhibitions[1], exhibition_cohort1)

        # Move user into cohort2, shows "no cohort" and cohort2
        self.user.cohort = cohort2
        self.user.save()
        response = client.post(create_url, post_data)
        exhibitions = response.context['form'].fields['exhibition'].queryset.all()
        self.assertEquals(len(exhibitions), 2)
        self.assertEquals(exhibitions[0], exhibition_no_cohort)
        self.assertEquals(exhibitions[1], exhibition_cohort2)

    def test_submit_unowned_artwork(self):
        client = Client()

        student_artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        staff_artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.staff_user)
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = timezone.now(),
            author=self.user)

        create_url = reverse('artwork-submit', kwargs={'artwork': student_artwork.id})
        self.assertLogin(client, create_url, user='staff')

        # Cannot submit others' artwork
        post_data = {
            'artwork': student_artwork.id,
            'exhibition': exhibition.id,
        }
        response = client.post(create_url, post_data)
        view_url = reverse('exhibition-view', kwargs={'pk':exhibition.id})
        self.assertEqual(response.status_code, 403)

        # Can submit own artwork
        post_data = {
            'artwork': staff_artwork.id,
            'exhibition': exhibition.id,
        }
        create_url = reverse('artwork-submit', kwargs={'artwork': staff_artwork.id})
        response = client.post(create_url, post_data)
        view_url = reverse('submission-view', kwargs={'pk':1})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure one submission is in the exhibition view list
        response = client.get(reverse('exhibition-view', kwargs={'pk':exhibition.id}))
        self.assertEquals(response.context['object'].id, exhibition.id)
        submissions = response.context['submissions']['object_list'].all()
        self.assertEquals(submissions.count(), 1)
        self.assertEquals(submissions[0].id, student_artwork.id)

    def test_super_cant_submit_any_artwork(self):
        client = Client()

        student_artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        super_artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.super_user)
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = timezone.now(),
            author=self.user)

        create_url = reverse('artwork-submit', kwargs={'artwork': student_artwork.id})
        self.assertLogin(client, create_url, user='super')

        # Cant's submit others' artwork
        post_data = {
            'artwork': student_artwork.id,
            'exhibition': exhibition.id,
        }
        response = client.post(create_url, post_data)
        self.assertEqual(response.status_code, 403)

        # Ensure no submissions in the exhibition view list
        view_url = reverse('exhibition-view', kwargs={'pk':exhibition.id})
        response = client.get(view_url)
        self.assertEquals(response.context['object'].id, exhibition.id)
        submissions = response.context['submissions']['object_list'].all()
        self.assertEquals(submissions.count(), 0)

        # Can submit own artwork
        post_data = {
            'artwork': super_artwork.id,
            'exhibition': exhibition.id,
        }
        create_url = reverse('artwork-submit', kwargs={'artwork': super_artwork.id})
        response = client.post(create_url, post_data)
        view_url = reverse('submission-view', kwargs={'pk':1})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure one submissions in the exhibition view list
        response = client.get(reverse('exhibition-view', kwargs={'pk':exhibition.id}))
        self.assertEquals(response.context['object'].id, exhibition.id)
        submissions = response.context['submissions']['object_list'].all()
        self.assertEquals(submissions.count(), 1)
        self.assertEquals(submissions[0].id, student_artwork.id)

    def test_submit_to_unreleased_exhibition(self):
        client = Client()

        student_artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = timezone.now() + timedelta(hours=24),
            author=self.user)
        self.assertFalse(exhibition.released_yet)

        create_url = reverse('artwork-submit', kwargs={'artwork': student_artwork.id})
        self.assertLogin(client, create_url)

        # Student cannot submit to unreleased exhibition
        post_data = {
            'artwork': student_artwork.id,
            'exhibition': exhibition.id,
        }
        response = client.post(create_url, post_data)
        self.assertEqual(response.status_code, 403)

        # But staff can
        self.assertLogin(client, create_url, user="staff")

        # Not by the student artwork submit URL either
        create_url = reverse('artwork-submit', kwargs={'artwork': student_artwork.id})
        post_data = {
            'artwork': student_artwork.id,
            'exhibition': exhibition.id,
        }
        response = client.post(create_url, post_data)
        view_url = reverse('exhibition-view', kwargs={'pk':exhibition.id})
        self.assertEquals(response.status_code, 403)

    def test_no_submit_twice(self):
        client = Client()

        student_artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = timezone.now(),
            author=self.user)

        create_url = reverse('artwork-submit', kwargs={'artwork': student_artwork.id})
        self.assertLogin(client, create_url)

        # Post submission
        post_data = {
            'artwork': student_artwork.id,
            'exhibition': exhibition.id,
        }
        response = client.post(create_url, post_data)
        view_url = reverse('submission-view', kwargs={'pk':1})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Submit same thing again
        response = client.post(create_url, post_data)
        self.assertRegexpMatches(response.content, r'Submission with this Exhibition and Artwork already exists.')

    def test_submit_shares_artwork(self):
        client = Client()

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        exhibition1 = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = timezone.now(),
            author=self.user)
        exhibition2 = Exhibition.objects.create(
            title='Another Exhibition',
            description='description goes here',
            released_at = timezone.now(),
            author=self.user)

        self.assertEqual(artwork.shared, 0)

        create_url = reverse('artwork-submit', kwargs={'artwork': artwork.id})
        self.assertLogin(client, create_url)

        # Post first submission
        post_data = {
            'artwork': artwork.id,
            'exhibition': exhibition1.id,
        }
        client.post(create_url, post_data)

        artwork = Artwork.objects.get(id=artwork.id)
        self.assertEqual(artwork.shared, 1)

        # Post second submission
        post_data = {
            'artwork': artwork.id,
            'exhibition': exhibition2.id,
        }
        client.post(create_url, post_data)

        artwork = Artwork.objects.get(id=artwork.id)
        self.assertEqual(artwork.shared, 2)

        # Duplicate submissions don't count
        client.post(create_url, post_data)

        artwork = Artwork.objects.get(id=artwork.id)
        self.assertEqual(artwork.shared, 2)


class SubmissionDeleteViewTest(UserSetUp, TestCase):

    def test_login(self):
        client = Client()
        delete_url = reverse('artwork-delete', kwargs={'pk': 1})
        response = client.get(delete_url)
        login_url = '%s?next=%s' % (reverse('login'), delete_url)
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)
        self.assertLogin(client, delete_url)

    def test_student_delete_own_submission(self):
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = timezone.now(),
            author=self.user)
        submission = Submission.objects.create(
            artwork=artwork,
            exhibition=exhibition,
            submitted_by=self.user)

        client = Client()
        delete_url = reverse('submission-delete', kwargs={'pk': submission.id})
        response = self.assertLogin(client, delete_url)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['object'].artwork, artwork)
        self.assertEquals(response.context['object'].exhibition, exhibition)

        # post redirects to artwork view
        response = client.post(delete_url)
        view_url = reverse('artwork-view', kwargs={'pk':artwork.id})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

    def test_student_cannot_delete_others_submission(self):
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.staff_user)
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = timezone.now(),
            author=self.staff_user)
        submission = Submission.objects.create(
            artwork=artwork,
            exhibition=exhibition,
            submitted_by=self.staff_user)

        client = Client()
        delete_url = reverse('submission-delete', kwargs={'pk': submission.id})
        response = self.assertLogin(client, delete_url)

        # delete error raises permission denied
        self.assertEquals(response.status_code, 403)

        # same if we post
        response = client.post(delete_url)
        self.assertEquals(response.status_code, 403)

    def test_staff_delete_student_submission(self):
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = timezone.now(),
            author=self.user)
        submission = Submission.objects.create(
            artwork=artwork,
            exhibition=exhibition,
            submitted_by=self.user)

        # staff can't submit student artworks
        client = Client()
        delete_url = reverse('submission-delete', kwargs={'pk': submission.id})
        response = self.assertLogin(client, delete_url, user="staff")
        self.assertEquals(response.status_code, 403)

        # post is also permission denied
        response = client.post(delete_url)
        self.assertEquals(response.status_code, 403)

    def test_super_delete_student_submission(self):
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = timezone.now(),
            author=self.user)
        submission = Submission.objects.create(
            artwork=artwork,
            exhibition=exhibition,
            submitted_by=self.user)

        # even super users can't delete student submissions
        client = Client()
        delete_url = reverse('submission-delete', kwargs={'pk': submission.id})
        response = self.assertLogin(client, delete_url, user="super")
        self.assertEquals(response.status_code, 403)

        # post is also permission denied
        response = client.post(delete_url)
        self.assertEquals(response.status_code, 403)

    def test_post_delete_votes(self):
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = timezone.now(),
            author=self.user)
        submission = Submission.objects.create(
            artwork=artwork,
            exhibition=exhibition,
            submitted_by=self.user)
        student_vote = Vote.objects.create(
            submission=submission,
            status=Vote.THUMBS_UP,
            voted_by=self.user)
        staff_vote = Vote.objects.create(
            submission=submission,
            status=Vote.THUMBS_UP,
            voted_by=self.staff_user)

        client = Client()
        self.assertLogin(client)

        self.assertEqual(Vote.objects.filter(submission=submission).count(), 2)

        delete_url = reverse('submission-delete', kwargs={'pk': submission.id})
        response = client.post(delete_url)
        view_url = reverse('artwork-view', kwargs={'pk':artwork.id})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        self.assertEqual(Vote.objects.filter(submission=submission).count(), 0)


    def test_get_no_delete_votes(self):
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = timezone.now(),
            author=self.user)
        submission = Submission.objects.create(
            artwork=artwork,
            exhibition=exhibition,
            submitted_by=self.user)
        student_vote = Vote.objects.create(
            submission=submission,
            status=Vote.THUMBS_UP,
            voted_by=self.user)
        staff_vote = Vote.objects.create(
            submission=submission,
            status=Vote.THUMBS_UP,
            voted_by=self.staff_user)

        client = Client()
        self.assertLogin(client)

        self.assertEqual(Vote.objects.filter(submission=submission).count(), 2)

        delete_url = reverse('submission-delete', kwargs={'pk': submission.id})
        response = client.get(delete_url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['object'].artwork, artwork)
        self.assertEquals(response.context['object'].exhibition, exhibition)

        self.assertEqual(Vote.objects.filter(submission=submission).count(), 2)

    def test_unsubmit_unshares_artwork(self):
        client = Client()

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        exhibition1 = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = timezone.now(),
            author=self.user)
        exhibition2 = Exhibition.objects.create(
            title='Another Exhibition',
            description='description goes here',
            released_at = timezone.now(),
            author=self.user)

        self.assertEqual(artwork.shared, 0)

        submission1 = Submission.objects.create(
            artwork=artwork,
            exhibition=exhibition1,
            submitted_by=self.user)
        artwork = Artwork.objects.get(id=artwork.id)
        self.assertEqual(artwork.shared, 1)

        submission2 = Submission.objects.create(
            artwork=artwork,
            exhibition=exhibition2,
            submitted_by=self.user)
        artwork = Artwork.objects.get(id=artwork.id)
        self.assertEqual(artwork.shared, 2)

        
        # Post first un-submission
        delete_url = reverse('submission-delete', kwargs={'pk': submission1.id})
        self.assertLogin(client, delete_url)
        client.post(delete_url, {})

        artwork = Artwork.objects.get(id=artwork.id)
        self.assertEqual(artwork.shared, 0)

        # Post second un-submission
        delete_url = reverse('submission-delete', kwargs={'pk': submission2.id})
        client.post(delete_url, {})

        artwork = Artwork.objects.get(id=artwork.id)
        self.assertEqual(artwork.shared, 0)

        # Re-deletes don't work
        client.post(delete_url, {})
        artwork = Artwork.objects.get(id=artwork.id)
        self.assertEqual(artwork.shared, 0)
