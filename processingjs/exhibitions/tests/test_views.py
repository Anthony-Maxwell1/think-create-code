from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.utils import timezone
from datetime import timedelta

from exhibitions.models import Exhibition
from uofa.test import UserSetUp


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

    def test_super_create_exhibition(self):
        
        client = Client()

        create_url = reverse('exhibition-add')
        response = client.get(create_url)

        # create requires login
        response = self.assertLogin(client, create_url, user='super')

        self.assertIn('title', response.context['form'].fields)
        self.assertIn('description', response.context['form'].fields)
        self.assertIn('released_at', response.context['form'].fields)
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
            'released_at': exhibition.released_at.strftime('%Y-%m-%d %H:%M:%S.%f'),
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
            'released_at': exhibition.released_at.strftime('%Y-%m-%d %H:%M:%S.%f'),
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
            'released_at': exhibition.released_at.strftime('%Y-%m-%d %H:%M:%S.%f'),
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
            'released_at': exhibition.released_at.strftime('%Y-%m-%d %H:%M:%S.%f'),
        }
        response = client.post(edit_url)
        self.assertRedirects(response, list_url, status_code=302, target_status_code=200)

        # Ensure the exhibition is unchanged
        view_url = reverse('exhibition-view', kwargs={'pk':exhibition.id})
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, exhibition.title)


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
