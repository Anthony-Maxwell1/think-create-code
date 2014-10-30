from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.utils import timezone
from datetime import timedelta

from gallery.tests import UserSetUp
from submissions.models import Submission
from exhibitions.models import Exhibition
from artwork.models import Artwork

class SubmissionListExhibitionViewTests(UserSetUp, TestCase):
    """Exhibition view includes Submission list."""

    def test_view(self):

        client = Client()

        # New exhibitions contain no submissions
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = timezone.now(),
            author=self.user)
        view_url = reverse('exhibition-view', kwargs={'pk': exhibition.id})

        response = client.get(view_url)
        self.assertEquals(response.context['object'].id, exhibition.id)
        self.assertEquals(response.context['object'].submission_set.count(), 0)

        # Submit an artwork to the exhibition to see it in the list
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        submission = Submission.objects.create(artwork=artwork, exhibition=exhibition, submitted_by=self.user)

        response = client.get(view_url)
        self.assertEquals(response.context['object'].id, exhibition.id)
        submissions = response.context['object'].submission_set.all()
        self.assertEquals(submissions.count(), 1)
        self.assertEquals(submissions[0].id, submission.id)


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

    def test_student_submit_own_artwork(self):
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
        view_url = reverse('exhibition-view', kwargs={'pk':exhibition.id})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure submission is in the exhibition view list
        response = client.get(view_url)
        self.assertEquals(response.context['object'].id, exhibition.id)
        submissions = response.context['object'].submission_set.all()
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


    def test_staff_submit_any_artwork(self):
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

        # Staff can submit student artwork
        post_data = {
            'artwork': student_artwork.id,
            'exhibition': exhibition.id,
        }
        response = client.post(create_url, post_data)
        view_url = reverse('exhibition-view', kwargs={'pk':exhibition.id})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure submission is in the exhibition view list
        response = client.get(view_url)
        self.assertEquals(response.context['object'].id, exhibition.id)
        submissions = response.context['object'].submission_set.all()
        self.assertEquals(submissions.count(), 1)
        self.assertEquals(submissions[0].id, student_artwork.id)

        # Staff can submit own artwork
        post_data = {
            'artwork': staff_artwork.id,
            'exhibition': exhibition.id,
        }
        create_url = reverse('artwork-submit', kwargs={'artwork': staff_artwork.id})
        response = client.post(create_url, post_data)
        view_url = reverse('exhibition-view', kwargs={'pk':exhibition.id})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure both submissions are in the exhibition view list
        response = client.get(view_url)
        self.assertEquals(response.context['object'].id, exhibition.id)
        submissions = response.context['object'].submission_set.all()
        self.assertEquals(submissions.count(), 2)
        self.assertEquals(submissions[0].id, student_artwork.id)
        self.assertEquals(submissions[1].id, staff_artwork.id)

    def test_super_submit_any_artwork(self):
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

        # Staff can submit student artwork
        post_data = {
            'artwork': student_artwork.id,
            'exhibition': exhibition.id,
        }
        response = client.post(create_url, post_data)
        view_url = reverse('exhibition-view', kwargs={'pk':exhibition.id})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure submission is in the exhibition view list
        response = client.get(view_url)
        self.assertEquals(response.context['object'].id, exhibition.id)
        submissions = response.context['object'].submission_set.all()
        self.assertEquals(submissions.count(), 1)
        self.assertEquals(submissions[0].id, student_artwork.id)

        # Staff can submit own artwork
        post_data = {
            'artwork': super_artwork.id,
            'exhibition': exhibition.id,
        }
        create_url = reverse('artwork-submit', kwargs={'artwork': super_artwork.id})
        response = client.post(create_url, post_data)
        view_url = reverse('exhibition-view', kwargs={'pk':exhibition.id})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure both submissions are in the exhibition view list
        response = client.get(view_url)
        self.assertEquals(response.context['object'].id, exhibition.id)
        submissions = response.context['object'].submission_set.all()
        self.assertEquals(submissions.count(), 2)
        self.assertEquals(submissions[0].id, student_artwork.id)
        self.assertEquals(submissions[1].id, super_artwork.id)

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
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

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

        # Student cannot submit to unreleased exhibition
        post_data = {
            'artwork': student_artwork.id,
            'exhibition': exhibition.id,
        }
        response = client.post(create_url, post_data)
        view_url = reverse('exhibition-view', kwargs={'pk':exhibition.id})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Submit same thing again
        response = client.post(create_url, post_data)
        self.assertRegexpMatches(response.content, r'Submission with this Exhibition and Artwork already exists.')


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

        client = Client()
        delete_url = reverse('submission-delete', kwargs={'pk': submission.id})
        response = self.assertLogin(client, delete_url, user="staff")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['object'].artwork, artwork)
        self.assertEquals(response.context['object'].exhibition, exhibition)

        # post redirects to artwork view
        response = client.post(delete_url)
        view_url = reverse('artwork-view', kwargs={'pk':artwork.id})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

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

        client = Client()
        delete_url = reverse('submission-delete', kwargs={'pk': submission.id})
        response = self.assertLogin(client, delete_url, user="super")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['object'].artwork, artwork)
        self.assertEquals(response.context['object'].exhibition, exhibition)

        # post redirects to artwork view
        response = client.post(delete_url)
        view_url = reverse('artwork-view', kwargs={'pk':artwork.id})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)
