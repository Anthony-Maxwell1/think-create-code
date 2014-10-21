from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.utils import timezone

from exhibitions.models import Exhibition
from gallery.tests import UserSetUp


class ExhibitionListTests(UserSetUp, TestCase):
    """Exhibition list view tests."""

    def test_list_view(self):
        
        client = Client()
        list_url = reverse('exhibition-list')
        response = client.get(list_url)

        self.assertEquals(list(response.context['object_list']), [])

        Exhibition.objects.create(title='New Exhibition', description='description goes here', author=self.user)
        response = client.get(list_url)
        self.assertEquals(response.context['object_list'].count(), 1)


class ExhibitionViewTests(UserSetUp, TestCase):
    """Exhibition view tests."""

    def test_view(self):
        
        client = Client()

        exhibition = Exhibition.objects.create(title='New Exhibition', description='description goes here', author=self.user)
        response = client.get(reverse('exhibition-view', kwargs={'pk':exhibition.id}))
        self.assertEquals(response.context['object'].title, exhibition.title)
        self.assertEquals(response.context['object'].description, exhibition.description)

    def test_view_not_found(self):
        
        client = Client()

        response = client.get(reverse('exhibition-view', kwargs={'pk':1}))
        self.assertEquals(response.status_code, 404)


class ExhibitionCreateTests(UserSetUp, TestCase):
    """Exhibition create view tests."""

    def test_create_exhibition(self):
        
        client = Client()

        create_url = reverse('exhibition-add')
        response = client.get(create_url)

        # create requires login
        login_url = '%s?next=%s' % (reverse('login'), create_url)
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)
        logged_in = client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in)

        response = client.get(create_url)
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


class ExhibitionEditTests(UserSetUp, TestCase):
    """Exhibition edit view tests."""

    def test_edit_exhibition(self):
        
        exhibition = Exhibition.objects.create(title='New Exhibition', description='description goes here', author=self.user)
        client = Client()

        edit_url = reverse('exhibition-edit', kwargs={'pk':exhibition.id})
        response = client.get(edit_url)

        # edit requires login
        login_url = '%s?next=%s' % (reverse('login'), edit_url)
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)
        logged_in = client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in)

        response = client.get(edit_url)
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


class ExhibitionDeleteTests(UserSetUp, TestCase):
    """Exhibition delete view tests."""

    def test_exhibition_in_the_context(self):
        
        client = Client()

        exhibition = Exhibition.objects.create(title='New Exhibition', description='description goes here', author=self.user)
        delete_url = reverse('exhibition-delete', kwargs={'pk':exhibition.id})
        response = client.get(delete_url)

        # delete requires login
        login_url = '%s?next=%s' % (reverse('login'), delete_url)
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)
        logged_in = client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in)

        response = client.get(delete_url)
        self.assertEquals(response.context['object'].title, exhibition.title)
        self.assertEquals(response.context['object'].description, exhibition.description)
