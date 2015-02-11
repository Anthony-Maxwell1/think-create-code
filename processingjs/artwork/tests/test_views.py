from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from artwork.models import Artwork
from uofa.test import UserSetUp


class ArtworkListTests(UserSetUp, TestCase):
    """Artwork list view tests."""

    def test_private_artwork(self):
        
        client = Client()
        list_path = reverse('artwork-list')
        response = client.get(list_path)

        self.assertEquals(list(response.context['object_list']), [])

        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)
        response = client.get(list_path)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['object_list'].count(), 0)

        # Can login to see my artwork, but no one else's
        response = self.assertLogin(client, list_path)
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork1)

    def test_shared_artwork(self):
        
        client = Client()
        list_path = reverse('artwork-list')
        response = client.get(list_path)

        self.assertEquals(list(response.context['object_list']), [])

        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', shared=1, author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', shared=1, author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', shared=1, author=self.super_user)

        # Shared artwork is visible to public
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 3)
        self.assertEquals(response.context['object_list'][0], artwork3)
        self.assertEquals(response.context['object_list'][1], artwork2)
        self.assertEquals(response.context['object_list'][2], artwork1)

        # Shared artwork + own private artwork is visible to logged-in users
        artwork4 = Artwork.objects.create(title='Artwork 4', code='// code goes here', shared=1, author=self.user)
        self.assertLogin(client)
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 4)
        self.assertEquals(response.context['object_list'][0], artwork4)
        self.assertEquals(response.context['object_list'][1], artwork3)
        self.assertEquals(response.context['object_list'][2], artwork2)
        self.assertEquals(response.context['object_list'][3], artwork1)

    def test_user_private_artwork(self):
        
        client = Client()

        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)

        list_path = reverse('artwork-author-list', kwargs={'author': self.staff_user.id})
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 0)

        list_path = reverse('artwork-author-list', kwargs={'author': self.super_user.id})
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 0)

        list_path = reverse('artwork-author-list', kwargs={'author': self.user.id})
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 0)

    def test_user_shared_artwork(self):
        
        client = Client()

        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', shared=1, author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', shared=1, author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', shared=1, author=self.super_user)

        # Shared artwork is visible to the public
        list_path = reverse('artwork-author-list', kwargs={'author': self.user.id})
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork1)

        list_path = reverse('artwork-author-list', kwargs={'author': self.staff_user.id})
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork2)

        list_path = reverse('artwork-author-list', kwargs={'author': self.super_user.id})
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork3)

    def test_studio_artwork(self):
        
        client = Client()

        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)

        # My Studio URL redirects to login page for unauthenticated users
        studio_path = reverse('artwork-studio')
        login_path = '%s?next=%s' % (reverse('login'), studio_path)
        response = client.get(studio_path)
        self.assertRedirects(response, login_path, status_code=302, target_status_code=200)

        # My Studio URL redirects to author list for authenticated users

        # Student login
        list_path = reverse('artwork-author-list', kwargs={'author': self.user.id, 'shared': 0})
        response = self.assertLogin(client, studio_path, user='student')
        self.assertRedirects(response, list_path, status_code=302, target_status_code=200)

        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork1)

        # Staff login
        list_path = reverse('artwork-author-list', kwargs={'author': self.staff_user.id, 'shared': 0})
        response = self.assertLogin(client, studio_path, user='staff')
        self.assertRedirects(response, list_path, status_code=302, target_status_code=200)

        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork2)

        # Super login
        list_path = reverse('artwork-author-list', kwargs={'author': self.super_user.id, 'shared': 0})
        response = self.assertLogin(client, studio_path, user='super')
        self.assertRedirects(response, list_path, status_code=302, target_status_code=200)

        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork3)

    def test_my_artwork(self):
        
        client = Client()

        # Author list shows only shared artwork

        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)

        list_path = reverse('artwork-author-list', kwargs={'author':self.user.id})
        response = self.assertLogin(client, list_path, user='student')
        self.assertEquals(response.context['object_list'].count(), 0)

        artwork1.shared = 1
        artwork1.save()
        response = self.assertLogin(client, list_path, user='student')
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork1)

        list_path = reverse('artwork-author-list', kwargs={'author':self.staff_user.id})
        response = self.assertLogin(client, list_path, user='staff')
        self.assertEquals(response.context['object_list'].count(), 0)

        artwork2.shared = 1
        artwork2.save()
        response = self.assertLogin(client, list_path, user='staff')
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork2)

        list_path = reverse('artwork-author-list', kwargs={'author':self.super_user.id})
        response = self.assertLogin(client, list_path, user='super')
        self.assertEquals(response.context['object_list'].count(), 0)

        artwork3.shared = 1
        artwork3.save()
        response = self.assertLogin(client, list_path, user='super')
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork3)


class ArtworkViewTests(UserSetUp, TestCase):
    """Artwork view tests."""

    def test_private_artwork(self):
        
        client = Client()

        # Artwork is private to the author (until submitted)
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        artwork_url = reverse('artwork-view', kwargs={'pk':artwork.id})
        response = client.get(artwork_url)
        login_url = '%s?next=%s' % (reverse('login'), artwork_url)
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)

        # Must login to see it
        response = self.assertLogin(client, artwork_url)
        self.assertEquals(response.context['object'].title, artwork.title)
        self.assertEquals(response.context['object'].code, artwork.code)
        self.assertIsNotNone(response.context['share_url'])

    def test_shared_artwork(self):
        
        client = Client()

        # Shared artwork is public (no login required)
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', shared=1, author=self.user)
        artwork_url = reverse('artwork-view', kwargs={'pk':artwork.id})
        response = client.get(artwork_url)
        self.assertEquals(response.context['object'].title, artwork.title)
        self.assertEquals(response.context['object'].code, artwork.code)
        self.assertIsNotNone(response.context['share_url'])

    def test_artwork_404(self):
        
        client = Client()
        response = client.get(reverse('artwork-view', kwargs={'pk':1}))
        self.assertEquals(response.status_code, 404)


class ArtworkViewRenderTests(UserSetUp, TestCase):
    """Artwork view render tests."""

    def test_artwork_render(self):
        
        client = Client()
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        response = client.get(reverse('artwork-render', kwargs={'pk':artwork.id}))

        # Template view contains no object data
        self.assertFalse('object' in response.context)

    def test_artwork_render_404(self):
        
        client = Client()
        response = client.get(reverse('artwork-render', kwargs={'pk':1}))
        # Template view doesn't care if the object doesn't exist
        self.assertEquals(response.status_code, 200)


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

        # however, we still can't delete the artwork, because we can't see it.
        view_url = reverse('artwork-view', kwargs={'pk':artwork.id})
        response = client.get(delete_url)
        self.assertRedirects(response, view_url, status_code=302, target_status_code=403)

        # nor by post
        response = client.post(delete_url)
        self.assertRedirects(response, view_url, status_code=302, target_status_code=403)

        # Ensure the artwork still exists (403 not 404)
        response = client.get(view_url)
        self.assertEquals(response.status_code, 403)

    def test_not_author_shared_delete(self):

        client = Client()

        otherUser = get_user_model().objects.create(username='other')
        artwork = Artwork.objects.create(title='Other User artwork', code='// code goes here', shared=1, author=otherUser)

        delete_url = reverse('artwork-delete', kwargs={'pk':artwork.id})
        response = client.get(delete_url)

        # delete requires login
        login_url = '%s?next=%s' % (reverse('login'), delete_url)
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)
        logged_in = client.login(username=self.get_username(), password=self.get_password())
        self.assertTrue(logged_in)

        # however, we still can't delete the artwork, because we don't own it
        view_url = reverse('artwork-view', kwargs={'pk':artwork.id})
        response = client.get(delete_url)
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # nor by post
        response = client.post(delete_url)
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Login to ensure the artwork still exists
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, artwork.title)


class ArtworkEditTests(UserSetUp, TestCase):
    """Artwork edit view tests."""

    def test_author_edit_unshared_artwork(self):
        
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)

        client = Client()

        view_url = reverse('artwork-view', kwargs={'pk':artwork.id})
        edit_url = reverse('artwork-edit', kwargs={'pk':artwork.id})
        login_url = '%s?next=%s' % (reverse('login'), edit_url)

        # Edit view for unshared artwork redirects to login
        response = client.get(edit_url)
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)

        # Post an update - unauthenticated redirects to login
        response = client.post(edit_url, {'title': 'My overridden title', 'code': artwork.code})
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)

        # Login as author
        response = self.assertLogin(client, edit_url)
        self.assertEquals(response.context['object'].title, artwork.title)
        self.assertEquals(response.context['object'].code, artwork.code)

        # Post an update - succeeds as author
        response = client.post(edit_url, {'title': 'My overridden title', 'code': artwork.code})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change was saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, 'My overridden title')

    def test_author_edit_shared_artwork(self):
        
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', shared=1, author=self.user)

        client = Client()

        view_url = reverse('artwork-view', kwargs={'pk':artwork.id})
        edit_url = reverse('artwork-edit', kwargs={'pk':artwork.id})
        login_url = '%s?next=%s' % (reverse('login'), edit_url)

        # Edit view for shared artwork allowed
        response = client.get(edit_url)
        self.assertEquals(response.status_code, 200)

        # Post an update - unauthenticated redirects to login
        response = client.post(edit_url, {'title': 'My overridden title', 'code': artwork.code})
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)

        # Login as author
        response = self.assertLogin(client, edit_url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['object'].title, artwork.title)
        self.assertEquals(response.context['object'].code, artwork.code)

        # Post an update - succeeds as author
        response = client.post(edit_url, {'title': 'My overridden title', 'code': artwork.code})
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Ensure the change was saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, 'My overridden title')

    def test_non_author_edit_unshared_artwork(self):
        
        # Create unshared artwork owned by another student user
        otherUser = get_user_model().objects.create(username='other')
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=otherUser)

        client = Client()

        view_url = reverse('artwork-view', kwargs={'pk':artwork.id})
        edit_url = reverse('artwork-edit', kwargs={'pk':artwork.id})
        login_url = '%s?next=%s' % (reverse('login'), edit_url)

        # Edit view for unshared artwork redirects to login
        response = client.get(edit_url)
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)

        # Post an update - unauthenticated redirects to login
        response = client.post(edit_url, {'title': 'My overridden title', 'code': artwork.code})
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)

        # Login as student - forbidden by non-author
        response = self.assertLogin(client, edit_url)
        self.assertEquals(response.status_code, 403)

        # Post an update - forbidden by non-authors
        response = client.post(edit_url, {'title': 'My overridden title', 'code': artwork.code})
        self.assertEquals(response.status_code, 403)

    def test_not_author_cant_edit_shared_artwork(self):
        
        # Create shared artwork owned by another student user
        otherUser = get_user_model().objects.create(username='other')
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', shared=1, author=otherUser)

        client = Client()

        view_url = reverse('artwork-view', kwargs={'pk':artwork.id})
        edit_url = reverse('artwork-edit', kwargs={'pk':artwork.id})
        login_url = '%s?next=%s' % (reverse('login'), edit_url)

        # Edit view for shared artwork allowed by anyone
        response = client.get(edit_url)
        self.assertEquals(response.context['object'].title, artwork.title)
        self.assertEquals(response.context['object'].code, artwork.code)

        # Post an update - unauthenticated redirects to login
        response = client.post(edit_url, {'title': 'My overridden title', 'code': artwork.code})
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)

        # login as non-author student
        self.assertLogin(client, edit_url)

        # Post an update - forbidden by non-authors
        response = client.post(edit_url, {'title': 'My overridden title', 'code': artwork.code})
        self.assertEquals(response.status_code, 403)

        # Ensure the change wasn't made
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, artwork.title)

    def test_non_author_staff_cant_edit_shared_artwork(self):
      
        # Create a student artwork
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', shared=1, author=self.user)

        client = Client()

        view_url = reverse('artwork-view', kwargs={'pk':artwork.id})
        edit_url = reverse('artwork-edit', kwargs={'pk':artwork.id})
        login_url = '%s?next=%s' % (reverse('login'), edit_url)

        # Edit view for shared artwork allowed by anyone
        response = client.get(edit_url)
        self.assertEquals(response.context['object'].title, artwork.title)
        self.assertEquals(response.context['object'].code, artwork.code)

        # Post an update - unauthenticated redirects to login
        response = client.post(edit_url, {'title': 'My overridden title', 'code': artwork.code})
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)

        # login as non-author staff
        self.assertLogin(client, edit_url, "staff")

        # Post an update - forbidden by non-authors
        response = client.post(edit_url, {'title': 'My overridden title', 'code': artwork.code})
        self.assertEquals(response.status_code, 403)

        # Ensure the change wasn't made
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, artwork.title)

    def test_non_author_super_cant_edit_shared_artwork(self):
      
        # Create a student artwork
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', shared=1, author=self.user)

        client = Client()

        view_url = reverse('artwork-view', kwargs={'pk':artwork.id})
        edit_url = reverse('artwork-edit', kwargs={'pk':artwork.id})
        login_url = '%s?next=%s' % (reverse('login'), edit_url)

        # Edit view for shared artwork allowed by anyone
        response = client.get(edit_url)
        self.assertEquals(response.context['object'].title, artwork.title)
        self.assertEquals(response.context['object'].code, artwork.code)

        # Post an update - unauthenticated redirects to login
        response = client.post(edit_url, {'title': 'My overridden title', 'code': artwork.code})
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)

        # login as non-author super
        self.assertLogin(client, edit_url, "super")

        # Post an update - forbidden by non-authors
        response = client.post(edit_url, {'title': 'My overridden title', 'code': artwork.code})
        self.assertEquals(response.status_code, 403)

        # Ensure the change wasn't made
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, artwork.title)

