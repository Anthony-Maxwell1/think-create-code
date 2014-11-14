from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from artwork.models import Artwork
from uofa.test import UserSetUp


class ArtworkListTests(UserSetUp, TestCase):
    """Artwork list view tests."""

    def test_artwork_in_the_context(self):
        
        client = Client()
        list_path = reverse('artwork-list')
        response = client.get(list_path)

        self.assertEquals(list(response.context['object_list']), [])

        Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 1)


class ArtworkViewTests(UserSetUp, TestCase):
    """Artwork view tests."""

    def test_artwork_in_the_context(self):
        
        client = Client()

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        response = client.get(reverse('artwork-view', kwargs={'pk':artwork.id}))
        self.assertEquals(response.context['object'].title, artwork.title)
        self.assertEquals(response.context['object'].code, artwork.code)

    def test_artwork_404(self):
        
        client = Client()
        response = client.get(reverse('artwork-view', kwargs={'pk':1}))
        self.assertEquals(response.status_code, 404)

class ArtworkViewCodeTests(UserSetUp, TestCase):
    """Artwork view code tests."""

    def test_artwork_code(self):
        
        client = Client()
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        response = client.get(reverse('artwork-code', kwargs={'pk':artwork.id}))
        self.assertEquals(response.content, "%s\n" % artwork.code)

    def test_artwork_code_404(self):
        
        client = Client()
        response = client.get(reverse('artwork-code', kwargs={'pk':1}))
        self.assertEquals(response.status_code, 404)



class ArtworkDeleteTests(UserSetUp, TestCase):
    """Artwork delete view tests."""

    def test_artwork_in_the_context(self):
        
        client = Client()

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        delete_url = reverse('artwork-delete', kwargs={'pk':artwork.id})
        response = client.get(delete_url)

        # delete requires login
        login_url = '%s?next=%s' % (reverse('login'), delete_url)
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)
        logged_in = client.login(username=self.get_username(), password=self.get_password())
        self.assertTrue(logged_in)

        response = client.get(delete_url)
        self.assertEquals(response.context['object'].title, artwork.title)
        self.assertEquals(response.context['object'].code, artwork.code)


    def test_not_author_delete(self):

        client = Client()

        otherUser = get_user_model().objects.create(username='other')
        artwork = Artwork.objects.create(title='Other User artwork', code='// code goes here', author=otherUser)

        delete_url = reverse('artwork-delete', kwargs={'pk':artwork.id})
        response = client.get(delete_url)

        # delete requires login
        login_url = '%s?next=%s' % (reverse('login'), delete_url)
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)
        logged_in = client.login(username=self.get_username(), password=self.get_password())
        self.assertTrue(logged_in)

        # however, we can't delete the artwork
        view_url = reverse('artwork-view', kwargs={'pk':artwork.id})
        response = client.get(delete_url)
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # nor by post
        response = client.post(delete_url)
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the artwork still exists
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, artwork.title)


class ArtworkEditTests(UserSetUp, TestCase):
    """Artwork edit view tests."""

    def test_edit_artwork(self):
        
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)

        client = Client()

        edit_url = reverse('artwork-edit', kwargs={'pk':artwork.id})
        response = client.get(edit_url)

        # edit requires login
        login_url = '%s?next=%s' % (reverse('login'), edit_url)
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)
        logged_in = client.login(username=self.get_username(), password=self.get_password())
        self.assertTrue(logged_in)

        response = client.get(edit_url)
        self.assertEquals(response.context['object'].title, artwork.title)
        self.assertEquals(response.context['object'].code, artwork.code)

        # Post an update
        response = client.post(edit_url, {'title': 'My overridden title', 'code': artwork.code})

        # Ensure the change was saved
        view_url = reverse('artwork-view', kwargs={'pk':artwork.id})
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, 'My overridden title')


    def test_not_author_edit_artwork(self):
        
        # Create a second user, and an artwork he owns
        otherUser = get_user_model().objects.create(username='other')
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=otherUser)

        client = Client()

        edit_url = reverse('artwork-edit', kwargs={'pk':artwork.id})
        response = client.get(edit_url)

        # edit requires login
        login_url = '%s?next=%s' % (reverse('login'), edit_url)
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)
        logged_in = client.login(username=self.get_username(), password=self.get_password())
        self.assertTrue(logged_in)

        # however, we can't edit the artwork
        view_url = reverse('artwork-view', kwargs={'pk':artwork.id})
        response = client.get(edit_url)
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # nor by post
        response = client.post(edit_url, {'title': 'My overridden title', 'code': artwork.code})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change wasn't made
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, artwork.title)
