from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.utils import timezone
from datetime import timedelta

from exhibitions.models import Exhibition
from django_adelaidex.lti.models import Cohort
from django_adelaidex.util.test import UserSetUp


class CohortMixin(object):
    '''Creates 2 cohorts'''

    def setUp(self):
        super(CohortMixin, self).setUp()
        self.cohort1 = Cohort.objects.create(
            title='Cohort 1',
            oauth_key='abc',
            oauth_secret='abc',
            is_default=True,
        )
        self.cohort2 = Cohort.objects.create(
            title='Cohort 2',
            oauth_key='def',
            oauth_secret='def',
        )

class ExhibitionCohortMixin(CohortMixin):
    '''Creates 3 exhibitions with the various cohort options'''

    def setUp(self):
        super(ExhibitionCohortMixin, self).setUp()
        self.exhibition_no_cohort = Exhibition.objects.create(
            title='Exhibition No Cohort',
            description='description goes here',
            author=self.user)
        self.exhibition_cohort1 = Exhibition.objects.create(
            title='Exhibition Cohort1',
            description='description goes here',
            cohort=self.cohort1,
            author=self.user)
        self.exhibition_cohort2 = Exhibition.objects.create(
            title='Exhibition Cohort2',
            description='description goes here',
            cohort=self.cohort2,
            author=self.user)


class ExhibitionListTests(UserSetUp, TestCase):
    """Exhibition list view tests."""

    def test_list_view(self):
        
        client = Client()
        list_url = reverse('exhibition-list')
        response = client.get(list_url)

        self.assertEquals(list(response.context['object_list']), [])

        now = timezone.now()
        today = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = now,
            author=self.user)
        response = client.get(list_url)
        self.assertEquals(response.context['object_list'].count(), 1)

    def test_list_view_after_release_date(self):
        
        client = Client()
        list_url = reverse('exhibition-list')
        response = client.get(list_url)

        self.assertEquals(list(response.context['object_list']), [])

        # Public can only see exhibitions whose release date has past
        now = timezone.now()
        yesterday = Exhibition.objects.create(
            title='Exhibition One',
            description='description goes here',
            released_at = now + timedelta(hours=-24),
            author=self.user)
        today = Exhibition.objects.create(
            title='Exhibition Two',
            description='description goes here',
            released_at = now,
            author=self.user)
        tomorrow = Exhibition.objects.create(
            title='Exhibition Three',
            description='description goes here',
            released_at = now + timedelta(hours=24),
            author=self.user)

        response = client.get(list_url)
        self.assertEquals(response.context['object_list'].count(), 2)
        self.assertEquals(response.context['object_list'][0].title, today.title)
        self.assertEquals(response.context['object_list'][1].title, yesterday.title)

        self.assertTrue(response.context['object_list'][0].released_yet)
        self.assertTrue(response.context['object_list'][1].released_yet)

    def test_list_view_staff(self):
        
        # Staff can see all exhibitions
        now = timezone.now()
        yesterday = Exhibition.objects.create(
            title='Exhibition One',
            description='description goes here',
            released_at = now + timedelta(hours=-24),
            author=self.user)
        today = Exhibition.objects.create(
            title='Exhibition Two',
            description='description goes here',
            released_at = now,
            author=self.user)
        tomorrow = Exhibition.objects.create(
            title='Exhibition Three',
            description='description goes here',
            released_at = now + timedelta(hours=24),
            author=self.user)

        client = Client()
        list_url = reverse('exhibition-list')
        response = self.assertLogin(client, list_url, user='staff')

        self.assertEquals(response.context['object_list'].count(), 3)
        self.assertEquals(response.context['object_list'][0].title, tomorrow.title)
        self.assertEquals(response.context['object_list'][1].title, today.title)
        self.assertEquals(response.context['object_list'][2].title, yesterday.title)

        self.assertFalse(response.context['object_list'][0].released_yet)
        self.assertTrue(response.context['object_list'][1].released_yet)
        self.assertTrue(response.context['object_list'][2].released_yet)

    def test_list_view_super(self):
        
        # Superusers can see all exhibitions
        now = timezone.now()
        yesterday = Exhibition.objects.create(
            title='Exhibition One',
            description='description goes here',
            released_at = now + timedelta(hours=-24),
            author=self.user)
        today = Exhibition.objects.create(
            title='Exhibition Two',
            description='description goes here',
            released_at = now,
            author=self.user)
        tomorrow = Exhibition.objects.create(
            title='Exhibition Three',
            description='description goes here',
            released_at = now + timedelta(hours=24),
            author=self.user)

        client = Client()
        list_url = reverse('exhibition-list')
        response = self.assertLogin(client, list_url, user='super')

        self.assertEquals(response.context['object_list'].count(), 3)
        self.assertEquals(response.context['object_list'][0].title, tomorrow.title)
        self.assertEquals(response.context['object_list'][1].title, today.title)
        self.assertEquals(response.context['object_list'][2].title, yesterday.title)

        self.assertFalse(response.context['object_list'][0].released_yet)
        self.assertTrue(response.context['object_list'][1].released_yet)
        self.assertTrue(response.context['object_list'][2].released_yet)

    def test_list_view_pk_list(self):
        
        client = Client()

        # Create three exhibitions
        now = timezone.now()
        exhibition1 = Exhibition.objects.create(
            title='Exhibition One',
            description='description goes here',
            released_at = now,
            author=self.user)

        exhibition2 = Exhibition.objects.create(
            title='Exhibition Two',
            description='description goes here',
            released_at = now,
            author=self.user)

        exhibition3 = Exhibition.objects.create(
            title='Exhibition Three',
            description='description goes here',
            released_at = now,
            author=self.user)

        pk_list = []
        list_url = reverse('exhibition-list', kwargs={'pk_list': ','.join(map(str,pk_list))})
        response = client.get(list_url)
        self.assertEquals(response.context['object_list'].count(), 3)
        self.assertEquals(response.context['object_list'][0].id, exhibition1.id)
        self.assertEquals(response.context['object_list'][1].id, exhibition2.id)
        self.assertEquals(response.context['object_list'][2].id, exhibition3.id)

        pk_list = [exhibition1.id, exhibition3.id]
        list_url = reverse('exhibition-list', kwargs={'pk_list': ','.join(map(str, pk_list))})
        response = client.get(list_url)
        self.assertEquals(response.context['object_list'].count(), 2)
        self.assertEquals(response.context['object_list'][0].id, pk_list[0])
        self.assertEquals(response.context['object_list'][1].id, pk_list[1])

        pk_list = [exhibition1.id, exhibition2.id]
        list_url = reverse('exhibition-list', kwargs={'pk_list': ','.join(map(str, pk_list))})
        response = client.get(list_url)
        self.assertEquals(response.context['object_list'].count(), 2)
        self.assertEquals(response.context['object_list'][0].id, pk_list[0])
        self.assertEquals(response.context['object_list'][1].id, pk_list[1])

        pk_list = [exhibition1.id, exhibition2.id, exhibition3.id]
        list_url = reverse('exhibition-list', kwargs={'pk_list': ','.join(map(str, pk_list))})
        response = client.get(list_url)
        self.assertEquals(response.context['object_list'].count(), 3)
        self.assertEquals(response.context['object_list'][0].id, pk_list[0])
        self.assertEquals(response.context['object_list'][1].id, pk_list[1])
        self.assertEquals(response.context['object_list'][2].id, pk_list[2])


class ExhibitionListCohortTests(ExhibitionCohortMixin, UserSetUp, TestCase):
    """Exhibition list view tests, with cohorts."""

    def test_list_view_cohort(self):
        
        # Public see only the no-cohort and default cohort exhibitions
        client = Client()
        list_url = reverse('exhibition-list')
        response = client.get(list_url)
        self.assertEquals(response.context['object_list'].count(), 2)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertIsNone(response.context['object_list'][0].cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort1)
        self.assertTrue(response.context['object_list'][1].cohort.is_default)

    def test_list_view_student_cohort(self):
        
        # Students see only the no-cohort and exhibitions in their cohort
        client = Client()
        list_url = reverse('exhibition-list')
        response = self.assertLogin(client, list_url, user='student')
        self.assertEquals(self.user.cohort, None)
        self.assertEquals(response.context['object_list'].count(), 2)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertIsNone(response.context['object_list'][0].cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort1)
        self.assertTrue(response.context['object_list'][1].cohort.is_default)

        # Put the student into cohort1, and she sees exhibitions with no cohort and cohort2
        self.user.cohort = self.cohort1
        self.user.save()
        response = client.get(list_url)
        self.assertEquals(response.context['object_list'].count(), 2)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertIsNone(response.context['object_list'][0].cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort1)
        self.assertTrue(response.context['object_list'][1].cohort.is_default)

        # Put the student into cohort2, and she sees exhibitions with no cohort and cohort2
        self.user.cohort = self.cohort2
        self.user.save()
        response = client.get(list_url)
        self.assertEquals(response.context['object_list'].count(), 2)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertIsNone(response.context['object_list'][0].cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort2)
        self.assertFalse(response.context['object_list'][1].cohort.is_default)

    def test_list_view_staff_cohort(self):
        
        # Staff see only the no-cohort and default cohort exhibitions
        client = Client()
        list_url = reverse('exhibition-list')
        response = self.assertLogin(client, list_url, user='staff')

        self.assertEquals(response.context['object_list'].count(), 2)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertIsNone(response.context['object_list'][0].cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort1)
        self.assertTrue(response.context['object_list'][1].cohort.is_default)

        # Put the staff user into cohort2, and she sees exhibitions with no cohort and cohort2
        self.staff_user.cohort = self.cohort2
        self.staff_user.save()
        response = client.get(list_url)
        self.assertEquals(response.context['object_list'].count(), 2)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertIsNone(response.context['object_list'][0].cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort2)
        self.assertFalse(response.context['object_list'][1].cohort.is_default)

    def test_list_view_super(self):
        
        # Superusers see all cohorts' exhibitions
        client = Client()
        list_url = reverse('exhibition-list')
        response = self.assertLogin(client, list_url, user='super')

        self.assertEquals(response.context['object_list'].count(), 3)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertIsNone(response.context['object_list'][0].cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort1)
        self.assertTrue(response.context['object_list'][1].cohort.is_default)
        self.assertEquals(response.context['object_list'][2], self.exhibition_cohort2)
        self.assertFalse(response.context['object_list'][2].cohort.is_default)

        self.super_user.cohort = self.cohort2
        self.super_user.save()
        response = client.get(list_url)
        self.assertEquals(response.context['object_list'].count(), 3)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertIsNone(response.context['object_list'][0].cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort1)
        self.assertTrue(response.context['object_list'][1].cohort.is_default)
        self.assertEquals(response.context['object_list'][2], self.exhibition_cohort2)
        self.assertFalse(response.context['object_list'][2].cohort.is_default)

    def test_list_view_pk_list_cohort(self):
        
        client = Client()

        # Even pk_list doesn't override cohort restrictions
        pk_list = []
        list_url = reverse('exhibition-list', kwargs={'pk_list': ','.join(map(str,pk_list))})
        response = client.get(list_url)
        self.assertEquals(response.context['object_list'].count(), 2)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertIsNone(response.context['object_list'][0].cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort1)
        self.assertTrue(response.context['object_list'][1].cohort.is_default)

        pk_list = [self.exhibition_no_cohort.id, self.exhibition_cohort1.id]
        list_url = reverse('exhibition-list', kwargs={'pk_list': ','.join(map(str, pk_list))})
        response = client.get(list_url)
        self.assertEquals(response.context['object_list'].count(), 2)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertIsNone(response.context['object_list'][0].cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort1)
        self.assertTrue(response.context['object_list'][1].cohort.is_default)

        pk_list = [self.exhibition_no_cohort.id, self.exhibition_cohort2.id]
        list_url = reverse('exhibition-list', kwargs={'pk_list': ','.join(map(str, pk_list))})
        response = client.get(list_url)
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertIsNone(response.context['object_list'][0].cohort)

        pk_list = [self.exhibition_no_cohort.id, self.exhibition_cohort1.id, self.exhibition_cohort2.id]
        list_url = reverse('exhibition-list', kwargs={'pk_list': ','.join(map(str, pk_list))})
        response = client.get(list_url)
        self.assertEquals(response.context['object_list'].count(), 2)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertIsNone(response.context['object_list'][0].cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort1)
        self.assertTrue(response.context['object_list'][1].cohort.is_default)


class ExhibitionViewTests(UserSetUp, TestCase):
    """Exhibition view tests."""

    def test_view(self):
        
        client = Client()

        exhibition = Exhibition.objects.create(title='New Exhibition', description='description goes here', author=self.user)
        response = client.get(reverse('exhibition-view', kwargs={'pk':exhibition.id}))
        self.assertEquals(response.context['object'].title, exhibition.title)
        self.assertEquals(response.context['object'].description, exhibition.description)
        self.assertTrue(response.context['object'].released_yet)

    def test_view_not_found(self):
        
        client = Client()

        response = client.get(reverse('exhibition-view', kwargs={'pk':1}))
        self.assertEquals(response.status_code, 404)

    def test_cannot_view_before_release_date(self):
        
        client = Client()

        now = timezone.now()
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = now + timedelta(hours=24),
            author=self.user)
        response = client.get(reverse('exhibition-view', kwargs={'pk':exhibition.id}))
        self.assertEquals(response.status_code, 403)

    def test_staff_view_before_release_date(self):
        
        client = Client()

        now = timezone.now()
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = now + timedelta(hours=24),
            author=self.user)
        self.assertLogin(client, user='staff')
        response = client.get(reverse('exhibition-view', kwargs={'pk':exhibition.id}))
        self.assertEquals(response.context['object'].title, exhibition.title)
        self.assertEquals(response.context['object'].description, exhibition.description)
        self.assertFalse(response.context['object'].released_yet)
        self.assertIsNotNone(response.context['share_url'])

    def test_super_view_before_release_date(self):
        
        client = Client()

        now = timezone.now()
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = now + timedelta(hours=24),
            author=self.user)
        self.assertLogin(client, user='super')
        response = client.get(reverse('exhibition-view', kwargs={'pk':exhibition.id}))
        self.assertEquals(response.context['object'].title, exhibition.title)
        self.assertEquals(response.context['object'].description, exhibition.description)
        self.assertFalse(response.context['object'].released_yet)
        self.assertIsNotNone(response.context['share_url'])


class ExhibitionViewCohortTests(ExhibitionCohortMixin, UserSetUp, TestCase):
    """Exhibition view tests, with cohorts."""

    def assert_can_view(self, client, exhibition):
        response = client.get(reverse('exhibition-view', kwargs={'pk':exhibition.id}))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['object'].title, exhibition.title)
        self.assertEquals(response.context['object'].description, exhibition.description)

    def assert_403(self, client, exhibition):
        response = client.get(reverse('exhibition-view', kwargs={'pk':exhibition.id}))
        self.assertEquals(response.status_code, 403)

    def test_public_view(self):
       
        # Public can only see no-cohort and default cohort exhibitions
        client = Client()
        self.assert_can_view(client, self.exhibition_no_cohort)
        self.assert_can_view(client, self.exhibition_cohort1)
        self.assert_403(client, self.exhibition_cohort2)

    def test_student_view(self):
       
        # Students can only see no-cohort and default cohort exhibitions
        client = Client()
        self.assertLogin(client, '/', user='student')

        self.assert_can_view(client, self.exhibition_no_cohort)
        self.assert_can_view(client, self.exhibition_cohort1)
        self.assert_403(client, self.exhibition_cohort2)

        # Move student into cohort 1, no change
        self.user.cohort = self.cohort1
        self.user.save()
        self.assert_can_view(client, self.exhibition_no_cohort)
        self.assert_can_view(client, self.exhibition_cohort1)
        self.assert_403(client, self.exhibition_cohort2)

        # Move student into cohort 2, and she can see cohort2 exhibitions but not cohort1
        self.user.cohort = self.cohort2
        self.user.save()
        self.assert_can_view(client, self.exhibition_no_cohort)
        self.assert_403(client, self.exhibition_cohort1)
        self.assert_can_view(client, self.exhibition_cohort2)

    def test_staff_view(self):

        # Staff can see exhibitions for all cohorts
        client = Client()
        self.assertLogin(client, '/', user='staff')

        self.assert_can_view(client, self.exhibition_no_cohort)
        self.assert_can_view(client, self.exhibition_cohort1)
        self.assert_can_view(client, self.exhibition_cohort2)

        # Move staff user into cohort 1, no change
        self.staff_user.cohort = self.cohort1
        self.staff_user.save()
        self.assert_can_view(client, self.exhibition_no_cohort)
        self.assert_can_view(client, self.exhibition_cohort1)
        self.assert_can_view(client, self.exhibition_cohort2)

        # Move staff user into cohort 2, no change
        self.staff_user.cohort = self.cohort2
        self.staff_user.save()
        self.assert_can_view(client, self.exhibition_no_cohort)
        self.assert_can_view(client, self.exhibition_cohort1)
        self.assert_can_view(client, self.exhibition_cohort2)

    def test_super_view(self):

        # Superusers can see exhibitions for all cohorts
        client = Client()
        self.assertLogin(client, '/', user='super')

        self.assert_can_view(client, self.exhibition_no_cohort)
        self.assert_can_view(client, self.exhibition_cohort1)
        self.assert_can_view(client, self.exhibition_cohort2)

        # Move superuser into cohort 1, no change
        self.super_user.cohort = self.cohort1
        self.super_user.save()
        self.assert_can_view(client, self.exhibition_no_cohort)
        self.assert_can_view(client, self.exhibition_cohort1)
        self.assert_can_view(client, self.exhibition_cohort2)

        # Move superuser into cohort 2, no change
        self.super_user.cohort = self.cohort2
        self.super_user.save()
        self.assert_can_view(client, self.exhibition_no_cohort)
        self.assert_can_view(client, self.exhibition_cohort1)
        self.assert_can_view(client, self.exhibition_cohort2)


class ExhibitionCreateTests(UserSetUp, TestCase):
    """Exhibition create view tests."""

    def test_staff_create_exhibition(self):
        
        client = Client()

        create_url = reverse('exhibition-add')
        response = client.get(create_url)

        # create requires login
        response = self.assertLogin(client, create_url, user='staff')

        self.assertIn('title', response.context['form'].fields)
        self.assertIn('description', response.context['form'].fields)
        self.assertIn('released_at', response.context['form'].fields)
        self.assertIn('cohort', response.context['form'].fields)
        self.assertNotIn('author', response.context['form'].fields)
        self.assertNotIn('created_at', response.context['form'].fields)
        self.assertNotIn('modified_at', response.context['form'].fields)

        # Post an update
        released_at = timezone.now()
        post_data = {
            'title': 'New Exhibition',
            'description': 'description goes here',
            'released_at': released_at.strftime('%Y-%m-%d %H:%M:%S.%f'),
        }
        response = client.post(create_url, post_data)

        # Ensure we're redirected to the view page for the new object
        view_url = reverse('exhibition-view', kwargs={'pk':1})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change was saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, post_data['title'])
        self.assertEquals(response.context['object'].description, post_data['description'])
        self.assertEquals(response.context['object'].released_at, released_at)
        self.assertEquals(response.context['object'].cohort, None)

    def test_super_create_exhibition(self):
        
        client = Client()

        create_url = reverse('exhibition-add')
        response = client.get(create_url)

        # create requires login
        response = self.assertLogin(client, create_url, user='super')

        self.assertIn('title', response.context['form'].fields)
        self.assertIn('description', response.context['form'].fields)
        self.assertIn('released_at', response.context['form'].fields)
        self.assertIn('cohort', response.context['form'].fields)
        self.assertNotIn('author', response.context['form'].fields)
        self.assertNotIn('created_at', response.context['form'].fields)
        self.assertNotIn('modified_at', response.context['form'].fields)

        # Post an update
        released_at = timezone.now()
        post_data = {
            'title': 'New Exhibition',
            'description': 'description goes here',
            'released_at': released_at.strftime('%Y-%m-%d %H:%M:%S.%f'),
        }
        response = client.post(create_url, post_data)

        # Ensure we're redirected to the view page for the new object
        view_url = reverse('exhibition-view', kwargs={'pk':1})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change was saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, post_data['title'])
        self.assertEquals(response.context['object'].description, post_data['description'])
        self.assertEquals(response.context['object'].released_at, released_at)
        self.assertEquals(response.context['object'].cohort, None)

    def test_students_cannot_create_exhibition(self):
        
        client = Client()

        create_url = reverse('exhibition-add')
        response = client.get(create_url)

        # create requires login
        response = self.assertLogin(client, create_url)
        list_url = reverse('exhibition-list')
        self.assertRedirects(response, list_url, status_code=302, target_status_code=200)

        # nor by post
        released_at = timezone.now()
        post_data = {
            'title': 'New Exhibition',
            'description': 'description goes here',
            'released_at': released_at.strftime('%Y-%m-%d %H:%M:%S.%f'),
        }
        response = client.post(create_url)
        self.assertRedirects(response, list_url, status_code=302, target_status_code=200)

        # ensure no exhibition was added
        response = client.get(list_url)
        self.assertEquals(list(response.context['object_list']), [])


class ExhibitionCreateCohortTests(CohortMixin, UserSetUp, TestCase):
    """Exhibition create view tests, with cohorts."""

    def test_students_cannot_create_exhibition(self):

        # students still cannot create exhibitions
        
        client = Client()

        create_url = reverse('exhibition-add')
        response = client.get(create_url)

        # create requires login
        response = self.assertLogin(client, create_url)
        list_url = reverse('exhibition-list')
        self.assertRedirects(response, list_url, status_code=302, target_status_code=200)

        # nor by post
        released_at = timezone.now()
        post_data = {
            'title': 'New Exhibition',
            'description': 'description goes here',
            'released_at': released_at.strftime('%Y-%m-%d %H:%M:%S.%f'),
        }
        response = client.post(create_url)
        self.assertRedirects(response, list_url, status_code=302, target_status_code=200)

        # ensure no exhibition was added
        response = client.get(list_url)
        self.assertEquals(list(response.context['object_list']), [])

    def test_staff_create_exhibition_cohort_form(self):

        # create requires login
        client = Client()
        create_url = reverse('exhibition-add')
        response = self.assertLogin(client, create_url, user='staff')

        self.assertIn('title', response.context['form'].fields)
        self.assertIn('description', response.context['form'].fields)
        self.assertIn('released_at', response.context['form'].fields)
        self.assertIn('cohort', response.context['form'].fields)
        self.assertNotIn('author', response.context['form'].fields)
        self.assertNotIn('created_at', response.context['form'].fields)
        self.assertNotIn('modified_at', response.context['form'].fields)

        # Ensure the default cohort is the initial value
        self.assertEqual(response.context['form'].initial['cohort'], self.cohort1.id)
        self.assertEqual(response.context['form'].fields['cohort'].empty_label, "Shared by all cohorts")
        
        # .. and that all the cohorts are available options
        choices = response.context['form'].fields['cohort'].choices
        self.assertEqual(len(choices), 3)
        choiceIter = iter(choices)
        self.assertEqual(choiceIter.next(), ('', "Shared by all cohorts"))
        self.assertEqual(choiceIter.next(), (self.cohort1.id, '%s' % self.cohort1))
        self.assertEqual(choiceIter.next(), (self.cohort2.id, '%s' % self.cohort2))

    def test_staff_create_exhibition_no_cohort(self):
        
        # create requires login
        client = Client()
        create_url = reverse('exhibition-add')
        response = self.assertLogin(client, create_url, user='staff')

        # Post create data with no cohort
        released_at = timezone.now()
        post_data = {
            'title': 'New Exhibition',
            'description': 'description goes here',
            'released_at': released_at.strftime('%Y-%m-%d %H:%M:%S.%f'),
            'cohort': '',
        }
        response = client.post(create_url, post_data)

        # Ensure we're redirected to the view page for the new object
        view_url = reverse('exhibition-view', kwargs={'pk':1})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change was saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, post_data['title'])
        self.assertEquals(response.context['object'].description, post_data['description'])
        self.assertEquals(response.context['object'].released_at, released_at)
        self.assertEquals(response.context['object'].cohort, None)

    def test_staff_create_exhibition_default_cohort(self):
        
        # create requires login
        client = Client()
        create_url = reverse('exhibition-add')
        response = self.assertLogin(client, create_url, user='staff')

        # Post create data with default cohort
        released_at = timezone.now()
        post_data = {
            'title': 'New Exhibition',
            'description': 'description goes here',
            'released_at': released_at.strftime('%Y-%m-%d %H:%M:%S.%f'),
            'cohort': self.cohort1.id,
        }
        response = client.post(create_url, post_data)

        # Ensure we're redirected to the view page for the new object
        view_url = reverse('exhibition-view', kwargs={'pk':1})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change was saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, post_data['title'])
        self.assertEquals(response.context['object'].description, post_data['description'])
        self.assertEquals(response.context['object'].released_at, released_at)
        self.assertEquals(response.context['object'].cohort, self.cohort1)

    def test_staff_create_exhibition_other_cohort(self):
        
        # create requires login
        client = Client()
        create_url = reverse('exhibition-add')
        response = self.assertLogin(client, create_url, user='staff')

        # Post create data with other cohort
        released_at = timezone.now()
        post_data = {
            'title': 'New Exhibition',
            'description': 'description goes here',
            'released_at': released_at.strftime('%Y-%m-%d %H:%M:%S.%f'),
            'cohort': self.cohort2.id,
        }
        response = client.post(create_url, post_data)

        # Ensure we're redirected to the view page for the new object
        view_url = reverse('exhibition-view', kwargs={'pk':1})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change was saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, post_data['title'])
        self.assertEquals(response.context['object'].description, post_data['description'])
        self.assertEquals(response.context['object'].released_at, released_at)
        self.assertEquals(response.context['object'].cohort, self.cohort2)

    def test_super_create_exhibition_cohort_form(self):

        # create requires login
        client = Client()
        create_url = reverse('exhibition-add')
        response = self.assertLogin(client, create_url, user='super')

        self.assertIn('title', response.context['form'].fields)
        self.assertIn('description', response.context['form'].fields)
        self.assertIn('released_at', response.context['form'].fields)
        self.assertIn('cohort', response.context['form'].fields)
        self.assertNotIn('author', response.context['form'].fields)
        self.assertNotIn('created_at', response.context['form'].fields)
        self.assertNotIn('modified_at', response.context['form'].fields)

        # Ensure the default cohort is the initial value
        self.assertEqual(response.context['form'].initial['cohort'], self.cohort1.id)
        self.assertEqual(response.context['form'].fields['cohort'].empty_label, "Shared by all cohorts")
        
        # .. and that all the cohorts are available options
        choices = response.context['form'].fields['cohort'].choices
        self.assertEqual(len(choices), 3)
        choiceIter = iter(choices)
        self.assertEqual(choiceIter.next(), ('', "Shared by all cohorts"))
        self.assertEqual(choiceIter.next(), (self.cohort1.id, '%s' % self.cohort1))
        self.assertEqual(choiceIter.next(), (self.cohort2.id, '%s' % self.cohort2))

    def test_super_create_exhibition_no_cohort(self):
        
        # create requires login
        client = Client()
        create_url = reverse('exhibition-add')
        response = self.assertLogin(client, create_url, user='super')

        # Post create data with no cohort
        released_at = timezone.now()
        post_data = {
            'title': 'New Exhibition',
            'description': 'description goes here',
            'released_at': released_at.strftime('%Y-%m-%d %H:%M:%S.%f'),
            'cohort': '',
        }
        response = client.post(create_url, post_data)

        # Ensure we're redirected to the view page for the new object
        view_url = reverse('exhibition-view', kwargs={'pk':1})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change was saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, post_data['title'])
        self.assertEquals(response.context['object'].description, post_data['description'])
        self.assertEquals(response.context['object'].released_at, released_at)
        self.assertEquals(response.context['object'].cohort, None)

    def test_super_create_exhibition_default_cohort(self):
        
        # create requires login
        client = Client()
        create_url = reverse('exhibition-add')
        response = self.assertLogin(client, create_url, user='super')

        # Post create data with default cohort
        released_at = timezone.now()
        post_data = {
            'title': 'New Exhibition',
            'description': 'description goes here',
            'released_at': released_at.strftime('%Y-%m-%d %H:%M:%S.%f'),
            'cohort': self.cohort1.id,
        }
        response = client.post(create_url, post_data)

        # Ensure we're redirected to the view page for the new object
        view_url = reverse('exhibition-view', kwargs={'pk':1})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change was saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, post_data['title'])
        self.assertEquals(response.context['object'].description, post_data['description'])
        self.assertEquals(response.context['object'].released_at, released_at)
        self.assertEquals(response.context['object'].cohort, self.cohort1)

    def test_super_create_exhibition_other_cohort(self):
        
        # create requires login
        client = Client()
        create_url = reverse('exhibition-add')
        response = self.assertLogin(client, create_url, user='super')

        # Post create data with other cohort
        released_at = timezone.now()
        post_data = {
            'title': 'New Exhibition',
            'description': 'description goes here',
            'released_at': released_at.strftime('%Y-%m-%d %H:%M:%S.%f'),
            'cohort': self.cohort2.id,
        }
        response = client.post(create_url, post_data)

        # Ensure we're redirected to the view page for the new object
        view_url = reverse('exhibition-view', kwargs={'pk':1})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change was saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, post_data['title'])
        self.assertEquals(response.context['object'].description, post_data['description'])
        self.assertEquals(response.context['object'].released_at, released_at)
        self.assertEquals(response.context['object'].cohort, self.cohort2)

class ExhibitionEditTests(UserSetUp, TestCase):
    """Exhibition edit view tests."""

    def test_staff_edit_own_exhibition(self):
        
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            author=self.staff_user)
        client = Client()

        edit_url = reverse('exhibition-edit', kwargs={'pk':exhibition.id})
        response = client.get(edit_url)

        # edit requires login
        response = self.assertLogin(client, edit_url, user='staff')
        self.assertEquals(response.context['object'].title, exhibition.title)
        self.assertEquals(response.context['object'].description, exhibition.description)

        # Post an update
        post_data = {
            'title': 'My overridden title',
            'description': exhibition.description,
        }
        response = client.post(edit_url, post_data)

        # Ensure we're redirected to the view page for the new object
        view_url = reverse('exhibition-view', kwargs={'pk':exhibition.id})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change was saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, post_data['title'])
        self.assertEquals(response.context['object'].description, post_data['description'])
        self.assertEquals(response.context['object'].released_at, exhibition.released_at)

    def test_staff_edit_any_exhibition(self):
        
        otherUser = get_user_model().objects.create(username='otherStaff', is_staff=True)
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            author=otherUser)
        client = Client()

        edit_url = reverse('exhibition-edit', kwargs={'pk':exhibition.id})
        response = client.get(edit_url)

        # edit requires login
        response = self.assertLogin(client, edit_url, user='staff')
        self.assertEquals(response.context['object'].title, exhibition.title)
        self.assertEquals(response.context['object'].description, exhibition.description)

        # Post an update
        post_data = {
            'title': 'My overridden title',
            'description': exhibition.description,
        }
        response = client.post(edit_url, post_data)

        # Ensure we're redirected to the view page for the new object
        view_url = reverse('exhibition-view', kwargs={'pk':exhibition.id})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change was saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, post_data['title'])
        self.assertEquals(response.context['object'].description, post_data['description'])
        self.assertEquals(response.context['object'].released_at, exhibition.released_at)

    def test_super_edit_any_exhibition(self):
        
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            author=self.staff_user)
        client = Client()

        edit_url = reverse('exhibition-edit', kwargs={'pk':exhibition.id})
        response = client.get(edit_url)

        # edit requires login
        response = self.assertLogin(client, edit_url, user='super')
        self.assertEquals(response.context['object'].title, exhibition.title)
        self.assertEquals(response.context['object'].description, exhibition.description)

        # Post an update
        post_data = {
            'title': 'My overridden title',
            'description': exhibition.description,
        }
        response = client.post(edit_url, post_data)

        # Ensure we're redirected to the view page for the new object
        view_url = reverse('exhibition-view', kwargs={'pk':exhibition.id})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change was saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, post_data['title'])
        self.assertEquals(response.context['object'].description, post_data['description'])
        self.assertEquals(response.context['object'].released_at, exhibition.released_at)

    def test_students_cannot_edit_exhibition(self):
        
        client = Client()
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            author=self.staff_user)

        edit_url = reverse('exhibition-edit', kwargs={'pk': exhibition.id})
        response = client.get(edit_url)

        # edit requires login
        response = self.assertLogin(client, edit_url)
        list_url = reverse('exhibition-list')
        self.assertRedirects(response, list_url, status_code=302, target_status_code=200)

        # nor by post
        post_data = {
            'title': 'My overridden title',
            'description': exhibition.description,
        }
        response = client.post(edit_url)
        self.assertRedirects(response, list_url, status_code=302, target_status_code=200)

        # Ensure the exhibition is unchanged
        view_url = reverse('exhibition-view', kwargs={'pk':exhibition.id})
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, exhibition.title)


class ExhibitionEditCohortTests(ExhibitionCohortMixin, UserSetUp, TestCase):
    """Exhibition edit view tests, with cohorts."""

    def test_staff_edit_exhibition_cohort_form(self):

        # create requires login
        client = Client()
        create_url = reverse('exhibition-add')
        response = self.assertLogin(client, create_url, user='staff')

        self.assertIn('title', response.context['form'].fields)
        self.assertIn('description', response.context['form'].fields)
        self.assertIn('released_at', response.context['form'].fields)
        self.assertIn('cohort', response.context['form'].fields)
        self.assertNotIn('author', response.context['form'].fields)
        self.assertNotIn('created_at', response.context['form'].fields)
        self.assertNotIn('modified_at', response.context['form'].fields)

        # Ensure the default cohort is the initial value
        self.assertEqual(response.context['form'].initial['cohort'], self.cohort1.id)
        self.assertEqual(response.context['form'].fields['cohort'].empty_label, "Shared by all cohorts")
        
        # .. and that all the cohorts are available options
        choices = response.context['form'].fields['cohort'].choices
        self.assertEqual(len(choices), 3)
        choiceIter = iter(choices)
        self.assertEqual(choiceIter.next(), ('', "Shared by all cohorts"))
        self.assertEqual(choiceIter.next(), (self.cohort1.id, '%s' % self.cohort1))
        self.assertEqual(choiceIter.next(), (self.cohort2.id, '%s' % self.cohort2))

    def test_staff_no_edit_cohort_exhibition(self):
        
        client = Client()

        edit_url = reverse('exhibition-edit', kwargs={'pk':self.exhibition_no_cohort.id})
        response = client.get(edit_url)

        # edit requires login
        response = self.assertLogin(client, edit_url, user='staff')
        self.assertEquals(response.context['object'].title, self.exhibition_no_cohort.title)
        self.assertEquals(response.context['object'].description, self.exhibition_no_cohort.description)
        self.assertEquals(response.context['object'].cohort, None)

        # Post an update to the cohort
        post_data = {
            'title': 'My overridden title',
            'description': self.exhibition_no_cohort.description,
        }
        response = client.post(edit_url, post_data)

        # Ensure we're redirected to the view page for the new object
        view_url = reverse('exhibition-view', kwargs={'pk':self.exhibition_no_cohort.id})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change was saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, post_data['title'])
        self.assertEquals(response.context['object'].description, post_data['description'])
        self.assertEquals(response.context['object'].released_at, self.exhibition_no_cohort.released_at)
        self.assertEquals(response.context['object'].cohort, None)

    def test_staff_edit_no_cohort_exhibition(self):
        
        client = Client()

        edit_url = reverse('exhibition-edit', kwargs={'pk':self.exhibition_no_cohort.id})
        response = client.get(edit_url)

        # edit requires login
        response = self.assertLogin(client, edit_url, user='staff')
        self.assertEquals(response.context['object'].title, self.exhibition_no_cohort.title)
        self.assertEquals(response.context['object'].description, self.exhibition_no_cohort.description)
        self.assertEquals(response.context['object'].cohort, None)

        # Post an update to the cohort
        post_data = {
            'title': 'My overridden title',
            'description': self.exhibition_no_cohort.description,
            'cohort': self.cohort1.id,
        }
        response = client.post(edit_url, post_data)

        # Ensure we're redirected to the view page for the new object
        view_url = reverse('exhibition-view', kwargs={'pk':self.exhibition_no_cohort.id})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change was saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, post_data['title'])
        self.assertEquals(response.context['object'].description, post_data['description'])
        self.assertEquals(response.context['object'].released_at, self.exhibition_no_cohort.released_at)
        self.assertEquals(response.context['object'].cohort, self.cohort1)

    def test_staff_edit_default_cohort_exhibition(self):
        
        client = Client()

        edit_url = reverse('exhibition-edit', kwargs={'pk':self.exhibition_cohort1.id})
        response = client.get(edit_url)

        # edit requires login
        response = self.assertLogin(client, edit_url, user='staff')
        self.assertEquals(response.context['object'].title, self.exhibition_cohort1.title)
        self.assertEquals(response.context['object'].description, self.exhibition_cohort1.description)
        self.assertEquals(response.context['object'].cohort, self.cohort1)

        # Post an update to the cohort
        post_data = {
            'title': 'My overridden title',
            'description': self.exhibition_cohort1.description,
            'cohort': self.cohort2.id,
        }
        response = client.post(edit_url, post_data)

        # Ensure we're redirected to the view page for the new object
        view_url = reverse('exhibition-view', kwargs={'pk':self.exhibition_cohort1.id})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change was saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, post_data['title'])
        self.assertEquals(response.context['object'].description, post_data['description'])
        self.assertEquals(response.context['object'].released_at, self.exhibition_cohort1.released_at)
        self.assertEquals(response.context['object'].cohort, self.cohort2)

    def test_super_no_edit_cohort_exhibition(self):
        
        client = Client()

        edit_url = reverse('exhibition-edit', kwargs={'pk':self.exhibition_no_cohort.id})
        response = client.get(edit_url)

        # edit requires login
        response = self.assertLogin(client, edit_url, user='super')
        self.assertEquals(response.context['object'].title, self.exhibition_no_cohort.title)
        self.assertEquals(response.context['object'].description, self.exhibition_no_cohort.description)
        self.assertEquals(response.context['object'].cohort, None)

        # Post an update to the cohort
        post_data = {
            'title': 'My overridden title',
            'description': self.exhibition_no_cohort.description,
        }
        response = client.post(edit_url, post_data)

        # Ensure we're redirected to the view page for the new object
        view_url = reverse('exhibition-view', kwargs={'pk':self.exhibition_no_cohort.id})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change was saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, post_data['title'])
        self.assertEquals(response.context['object'].description, post_data['description'])
        self.assertEquals(response.context['object'].released_at, self.exhibition_no_cohort.released_at)
        self.assertEquals(response.context['object'].cohort, None)

    def test_super_edit_no_cohort_exhibition(self):
        
        client = Client()

        edit_url = reverse('exhibition-edit', kwargs={'pk':self.exhibition_no_cohort.id})
        response = client.get(edit_url)

        # edit requires login
        response = self.assertLogin(client, edit_url, user='super')
        self.assertEquals(response.context['object'].title, self.exhibition_no_cohort.title)
        self.assertEquals(response.context['object'].description, self.exhibition_no_cohort.description)
        self.assertEquals(response.context['object'].cohort, None)

        # Post an update to the cohort
        post_data = {
            'title': 'My overridden title',
            'description': self.exhibition_no_cohort.description,
            'cohort': self.cohort1.id,
        }
        response = client.post(edit_url, post_data)

        # Ensure we're redirected to the view page for the new object
        view_url = reverse('exhibition-view', kwargs={'pk':self.exhibition_no_cohort.id})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change was saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, post_data['title'])
        self.assertEquals(response.context['object'].description, post_data['description'])
        self.assertEquals(response.context['object'].released_at, self.exhibition_no_cohort.released_at)
        self.assertEquals(response.context['object'].cohort, self.cohort1)

    def test_super_edit_default_cohort_exhibition(self):
        
        client = Client()

        edit_url = reverse('exhibition-edit', kwargs={'pk':self.exhibition_cohort1.id})
        response = client.get(edit_url)

        # edit requires login
        response = self.assertLogin(client, edit_url, user='super')
        self.assertEquals(response.context['object'].title, self.exhibition_cohort1.title)
        self.assertEquals(response.context['object'].description, self.exhibition_cohort1.description)
        self.assertEquals(response.context['object'].cohort, self.cohort1)

        # Post an update to the cohort
        post_data = {
            'title': 'My overridden title',
            'description': self.exhibition_cohort1.description,
            'cohort': self.cohort2.id,
        }
        response = client.post(edit_url, post_data)

        # Ensure we're redirected to the view page for the new object
        view_url = reverse('exhibition-view', kwargs={'pk':self.exhibition_cohort1.id})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change was saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, post_data['title'])
        self.assertEquals(response.context['object'].description, post_data['description'])
        self.assertEquals(response.context['object'].released_at, self.exhibition_cohort1.released_at)
        self.assertEquals(response.context['object'].cohort, self.cohort2)

    def test_students_cannot_edit_exhibition(self):

        # Students still cannot edit exhibitions with cohorts
        
        client = Client()
        edit_url = reverse('exhibition-edit', kwargs={'pk': self.exhibition_cohort1.id})
        response = client.get(edit_url)

        # edit requires login
        response = self.assertLogin(client, edit_url)
        list_url = reverse('exhibition-list')
        self.assertRedirects(response, list_url, status_code=302, target_status_code=200)

        # nor by post
        post_data = {
            'title': 'My overridden title',
            'description': self.exhibition_cohort1.description,
        }
        response = client.post(edit_url)
        self.assertRedirects(response, list_url, status_code=302, target_status_code=200)

        # Ensure the exhibition is unchanged
        view_url = reverse('exhibition-view', kwargs={'pk':self.exhibition_cohort1.id})
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, self.exhibition_cohort1.title)


class ExhibitionDeleteTests(UserSetUp, TestCase):
    """Exhibition delete view tests."""

    def test_staff_delete_own_exhibition(self):
        
        client = Client()

        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            author=self.staff_user)
        delete_url = reverse('exhibition-delete', kwargs={'pk':exhibition.id})
        response = client.get(delete_url)

        # delete requires login
        response = self.assertLogin(client, delete_url, user='staff')
        self.assertEquals(response.context['object'].title, exhibition.title)
        self.assertEquals(response.context['object'].description, exhibition.description)

    def test_staff_delete_any_exhibition(self):
        
        client = Client()
        otherUser = get_user_model().objects.create(username='otherStaff', is_staff=True)

        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            author=otherUser)
        delete_url = reverse('exhibition-delete', kwargs={'pk':exhibition.id})
        response = client.get(delete_url)

        # delete requires login
        response = self.assertLogin(client, delete_url, user='staff')
        self.assertEquals(response.context['object'].title, exhibition.title)
        self.assertEquals(response.context['object'].description, exhibition.description)

    def test_super_delete_any_exhibition(self):
        
        client = Client()
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            author=self.staff_user)
        delete_url = reverse('exhibition-delete', kwargs={'pk':exhibition.id})
        response = client.get(delete_url)

        # delete requires login
        response = self.assertLogin(client, delete_url, user='super')
        self.assertEquals(response.context['object'].title, exhibition.title)
        self.assertEquals(response.context['object'].description, exhibition.description)

    def test_students_cannot_delete_exhibition(self):
        
        client = Client()

        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            author=self.staff_user)
        delete_url = reverse('exhibition-delete', kwargs={'pk':exhibition.id})
        response = client.get(delete_url)

        # delete requires login
        response = self.assertLogin(client, delete_url, user='student')

        # still can't see delete page
        list_url = reverse('exhibition-list')
        self.assertRedirects(response, list_url, status_code=302, target_status_code=200)

        # nor by post
        response = client.post(delete_url)
        self.assertRedirects(response, list_url, status_code=302, target_status_code=200)

        # Ensure the exhibition still exists
        view_url = reverse('exhibition-view', kwargs={'pk':exhibition.id})
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, exhibition.title)


class ExhibitionDeleteCohortTests(ExhibitionCohortMixin, UserSetUp, TestCase):
    """Exhibition delete view tests, with cohorts"""

    def test_students_cannot_delete_exhibition(self):

        # Students still cannot delete exhibitions with cohorts
        client = Client()

        delete_url = reverse('exhibition-delete', kwargs={'pk':self.exhibition_cohort1.id})
        response = client.get(delete_url)

        # delete requires login
        response = self.assertLogin(client, delete_url, user='student')

        # still can't see delete page
        list_url = reverse('exhibition-list')
        self.assertRedirects(response, list_url, status_code=302, target_status_code=200)

        # nor by post
        response = client.post(delete_url)
        self.assertRedirects(response, list_url, status_code=302, target_status_code=200)

        # Ensure the exhibition still exists
        view_url = reverse('exhibition-view', kwargs={'pk':self.exhibition_cohort1.id})
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, self.exhibition_cohort1.title)

    def test_staff_delete_no_cohort(self):
        
        client = Client()

        # Starting with 2 visible
        list_url = reverse('exhibition-list')
        response = self.assertLogin(client, list_url, user='staff')
        self.assertEquals(len(response.context['object_list']), 2)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort1)

        delete_url = reverse('exhibition-delete', kwargs={'pk':self.exhibition_no_cohort.id})
        response = client.get(delete_url)

        # delete requires login
        response = client.get(delete_url)
        self.assertEquals(response.context['object'].title, self.exhibition_no_cohort.title)
        self.assertEquals(response.context['object'].description, self.exhibition_no_cohort.description)
        self.assertEquals(response.context['object'].cohort, None)

        # perform the post
        response = client.post(delete_url)
        self.assertRedirects(response, list_url, status_code=302, target_status_code=200)

        # Ensure the no-cohort exhibition is no longer in the list
        response = client.get(list_url)
        self.assertEquals(len(response.context['object_list']), 1)
        self.assertEquals(response.context['object_list'][0], self.exhibition_cohort1)

    def test_staff_delete_cohort1(self):
        
        client = Client()

        # Starting with 2 visible
        list_url = reverse('exhibition-list')
        response = self.assertLogin(client, list_url, user='staff')
        self.assertEquals(len(response.context['object_list']), 2)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort1)

        delete_url = reverse('exhibition-delete', kwargs={'pk':self.exhibition_cohort1.id})
        response = client.get(delete_url)

        # delete requires login
        response = client.get(delete_url)
        self.assertEquals(response.context['object'].title, self.exhibition_cohort1.title)
        self.assertEquals(response.context['object'].description, self.exhibition_cohort1.description)
        self.assertEquals(response.context['object'].cohort, self.cohort1)

        # perform the post
        response = client.post(delete_url)
        self.assertRedirects(response, list_url, status_code=302, target_status_code=200)

        # Ensure the no-cohort exhibition is no longer in the list
        response = client.get(list_url)
        self.assertEquals(len(response.context['object_list']), 1)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)

    def test_staff_delete_cohort2(self):
        
        client = Client()

        # Starting with 2 visible
        list_url = reverse('exhibition-list')
        response = self.assertLogin(client, list_url, user='staff')
        self.assertEquals(len(response.context['object_list']), 2)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort1)

        delete_url = reverse('exhibition-delete', kwargs={'pk':self.exhibition_cohort2.id})
        response = client.get(delete_url)

        # delete requires login
        response = client.get(delete_url)
        self.assertEquals(response.context['object'].title, self.exhibition_cohort2.title)
        self.assertEquals(response.context['object'].description, self.exhibition_cohort2.description)
        self.assertEquals(response.context['object'].cohort, self.cohort2)

        # perform the post
        response = client.post(delete_url)
        self.assertRedirects(response, list_url, status_code=302, target_status_code=200)

        # Ensure the no-cohort exhibition is no longer in the list
        response = client.get(list_url)
        self.assertEquals(len(response.context['object_list']), 2)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort1)

    def test_super_delete_no_cohort(self):
        
        client = Client()

        # Starting with 2 visible
        list_url = reverse('exhibition-list')
        response = self.assertLogin(client, list_url, user='super')
        self.assertEquals(len(response.context['object_list']), 3)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort1)
        self.assertEquals(response.context['object_list'][2], self.exhibition_cohort2)

        delete_url = reverse('exhibition-delete', kwargs={'pk':self.exhibition_no_cohort.id})
        response = client.get(delete_url)

        # delete requires login
        response = client.get(delete_url)
        self.assertEquals(response.context['object'].title, self.exhibition_no_cohort.title)
        self.assertEquals(response.context['object'].description, self.exhibition_no_cohort.description)
        self.assertEquals(response.context['object'].cohort, None)

        # perform the post
        response = client.post(delete_url)
        self.assertRedirects(response, list_url, status_code=302, target_status_code=200)

        # Ensure the no-cohort exhibition is no longer in the list
        response = client.get(list_url)
        self.assertEquals(len(response.context['object_list']), 2)
        self.assertEquals(response.context['object_list'][0], self.exhibition_cohort1)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort2)

    def test_super_delete_cohort1(self):
        
        client = Client()

        # Starting with 2 visible
        list_url = reverse('exhibition-list')
        response = self.assertLogin(client, list_url, user='super')
        self.assertEquals(len(response.context['object_list']), 3)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort1)
        self.assertEquals(response.context['object_list'][2], self.exhibition_cohort2)

        delete_url = reverse('exhibition-delete', kwargs={'pk':self.exhibition_cohort1.id})
        response = client.get(delete_url)

        # delete requires login
        response = client.get(delete_url)
        self.assertEquals(response.context['object'].title, self.exhibition_cohort1.title)
        self.assertEquals(response.context['object'].description, self.exhibition_cohort1.description)
        self.assertEquals(response.context['object'].cohort, self.cohort1)

        # perform the post
        response = client.post(delete_url)
        self.assertRedirects(response, list_url, status_code=302, target_status_code=200)

        # Ensure the no-cohort exhibition is no longer in the list
        response = client.get(list_url)
        self.assertEquals(len(response.context['object_list']), 2)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort2)

    def test_super_delete_cohort2(self):
        
        client = Client()

        # Starting with 2 visible
        list_url = reverse('exhibition-list')
        response = self.assertLogin(client, list_url, user='super')
        self.assertEquals(len(response.context['object_list']), 3)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort1)
        self.assertEquals(response.context['object_list'][2], self.exhibition_cohort2)

        delete_url = reverse('exhibition-delete', kwargs={'pk':self.exhibition_cohort2.id})
        response = client.get(delete_url)

        # delete requires login
        response = client.get(delete_url)
        self.assertEquals(response.context['object'].title, self.exhibition_cohort2.title)
        self.assertEquals(response.context['object'].description, self.exhibition_cohort2.description)
        self.assertEquals(response.context['object'].cohort, self.cohort2)

        # perform the post
        response = client.post(delete_url)
        self.assertRedirects(response, list_url, status_code=302, target_status_code=200)

        # Ensure the no-cohort exhibition is no longer in the list
        response = client.get(list_url)
        self.assertEquals(len(response.context['object_list']), 2)
        self.assertEquals(response.context['object_list'][0], self.exhibition_no_cohort)
        self.assertEquals(response.context['object_list'][1], self.exhibition_cohort1)
