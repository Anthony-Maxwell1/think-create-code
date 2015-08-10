from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from artwork.models import Artwork
from exhibitions.models import Exhibition
from submissions.models import Submission
from votes.models import Vote
from django_adelaidex.util.test import UserSetUp
import re


class ArtworkListTests(UserSetUp, TestCase):
    """Artwork list view tests."""

    def test_private_artwork_list(self):
        
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
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-list-zip'))

        # Can login to see my artwork, but no one else's
        response = self.assertLogin(client, list_path)
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork1)
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-list-zip'))

    def test_shared_artwork_list(self):
        
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
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-list-zip'))

        # Shared artwork + own private artwork is visible to logged-in users
        artwork4 = Artwork.objects.create(title='Artwork 4', code='// code goes here', shared=1, author=self.user)
        self.assertLogin(client)
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 4)
        self.assertEquals(response.context['object_list'][0], artwork4)
        self.assertEquals(response.context['object_list'][1], artwork3)
        self.assertEquals(response.context['object_list'][2], artwork2)
        self.assertEquals(response.context['object_list'][3], artwork1)
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-list-zip'))

    def test_artwork_shared_list(self):
        
        client = Client()
        list_path = reverse('artwork-shared')
        response = client.get(list_path)

        self.assertEquals(list(response.context['object_list']), [])

        artwork1p = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', shared=1, author=self.user)
        artwork2p = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', shared=1, author=self.staff_user)
        artwork3p = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', shared=1, author=self.super_user)

        # Shared artwork is visible to public
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 3)
        self.assertEquals(response.context['object_list'][0], artwork3)
        self.assertEquals(response.context['object_list'][1], artwork2)
        self.assertEquals(response.context['object_list'][2], artwork1)
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-shared-zip'))

        # Only shared artwork is visible to logged-in users in artwork-shared view
        response = self.assertLogin(client, list_path)
        self.assertEquals(response.context['object_list'].count(), 3)
        self.assertEquals(response.context['object_list'][0], artwork3)
        self.assertEquals(response.context['object_list'][1], artwork2)
        self.assertEquals(response.context['object_list'][2], artwork1)
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-shared-zip'))

        response = self.assertLogin(client, list_path, user='staff')
        self.assertEquals(response.context['object_list'].count(), 3)
        self.assertEquals(response.context['object_list'][0], artwork3)
        self.assertEquals(response.context['object_list'][1], artwork2)
        self.assertEquals(response.context['object_list'][2], artwork1)
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-shared-zip'))

        response = self.assertLogin(client, list_path, user='super')
        self.assertEquals(response.context['object_list'].count(), 3)
        self.assertEquals(response.context['object_list'][0], artwork3)
        self.assertEquals(response.context['object_list'][1], artwork2)
        self.assertEquals(response.context['object_list'][2], artwork1)
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-shared-zip'))

    def test_private_artwork_author_list(self):
        
        client = Client()

        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)

        list_kwargs = {'author': self.staff_user.id}
        list_path = reverse('artwork-author-list', kwargs=list_kwargs)
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 0)
        list_kwargs['shared'] = response.context['shared']
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-author-list-zip', kwargs=list_kwargs))

        list_kwargs = {'author': self.super_user.id}
        list_path = reverse('artwork-author-list', kwargs=list_kwargs)
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 0)
        list_kwargs['shared'] = response.context['shared']
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-author-list-zip', kwargs=list_kwargs))

        list_kwargs = {'author': self.user.id}
        list_path = reverse('artwork-author-list', kwargs=list_kwargs)
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 0)
        list_kwargs['shared'] = response.context['shared']
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-author-list-zip', kwargs=list_kwargs))

    def test_shared_artwork_author_list(self):
        
        client = Client()

        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', shared=1, author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', shared=1, author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', shared=1, author=self.super_user)

        # Shared artwork is visible to the public
        list_kwargs = {'author': self.user.id}
        list_path = reverse('artwork-author-list', kwargs=list_kwargs)
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork1)
        list_kwargs['shared'] = response.context['shared']
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-author-list-zip', kwargs=list_kwargs))

        list_kwargs = {'author': self.staff_user.id}
        list_path = reverse('artwork-author-list', kwargs=list_kwargs)
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork2)
        list_kwargs['shared'] = response.context['shared']
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-author-list-zip', kwargs=list_kwargs))

        list_kwargs = {'author': self.super_user.id}
        list_path = reverse('artwork-author-list', kwargs=list_kwargs)
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork3)
        list_kwargs['shared'] = response.context['shared']
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-author-list-zip', kwargs=list_kwargs))

    def test_artwork_studio(self):
        
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
        list_kwargs = {'author': self.user.id, 'shared': 0}
        list_path = reverse('artwork-author-list', kwargs=list_kwargs)
        response = self.assertLogin(client, studio_path, user='student')
        self.assertRedirects(response, list_path, status_code=302, target_status_code=200)

        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork1)
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-author-list-zip', kwargs=list_kwargs))

        # Staff login
        list_kwargs = {'author': self.staff_user.id, 'shared': 0}
        list_path = reverse('artwork-author-list', kwargs=list_kwargs)
        response = self.assertLogin(client, studio_path, user='staff')
        self.assertRedirects(response, list_path, status_code=302, target_status_code=200)

        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork2)
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-author-list-zip', kwargs=list_kwargs))

        # Super login
        list_kwargs = {'author': self.super_user.id, 'shared': 0}
        list_path = reverse('artwork-author-list', kwargs=list_kwargs)
        response = self.assertLogin(client, studio_path, user='super')
        self.assertRedirects(response, list_path, status_code=302, target_status_code=200)

        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork3)
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-author-list-zip', kwargs=list_kwargs))

    def test_my_artwork_author_list(self):
        
        client = Client()

        # Author list shows only shared artwork

        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)

        list_kwargs = {'author': self.user.id}
        list_path = reverse('artwork-author-list', kwargs=list_kwargs)
        response = self.assertLogin(client, list_path, user='student')
        self.assertEquals(response.context['object_list'].count(), 0)
        list_kwargs['shared'] = response.context['shared']
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-author-list-zip', kwargs=list_kwargs))

        artwork1.shared = 1
        artwork1.save()
        response = self.assertLogin(client, list_path, user='student')
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork1)
        list_kwargs['shared'] = response.context['shared']
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-author-list-zip', kwargs=list_kwargs))

        list_kwargs = {'author': self.staff_user.id}
        list_path = reverse('artwork-author-list', kwargs=list_kwargs)
        response = self.assertLogin(client, list_path, user='staff')
        self.assertEquals(response.context['object_list'].count(), 0)
        list_kwargs['shared'] = response.context['shared']
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-author-list-zip', kwargs=list_kwargs))

        artwork2.shared = 1
        artwork2.save()
        response = self.assertLogin(client, list_path, user='staff')
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork2)
        list_kwargs['shared'] = response.context['shared']
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-author-list-zip', kwargs=list_kwargs))

        list_kwargs = {'author': self.super_user.id}
        list_path = reverse('artwork-author-list', kwargs={'author':self.super_user.id})
        response = self.assertLogin(client, list_path, user='super')
        self.assertEquals(response.context['object_list'].count(), 0)
        list_kwargs['shared'] = response.context['shared']
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-author-list-zip', kwargs=list_kwargs))

        artwork3.shared = 1
        artwork3.save()
        response = self.assertLogin(client, list_path, user='super')
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0], artwork3)
        list_kwargs['shared'] = response.context['shared']
        self.assertEquals(response.context['zip_file_url'], reverse('artwork-author-list-zip', kwargs=list_kwargs))


class SubmittedArtworkListTests(UserSetUp, TestCase):

    def setUp(self):
        super(SubmittedArtworkListTests, self).setUp()

        self.artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        self.artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.user)
        self.exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            author=self.user)
        self.submission1 = Submission.objects.create(
            artwork=self.artwork1,
            exhibition=self.exhibition,
            submitted_by=self.user)
        vote1 = Vote.objects.create(submission=self.submission1,
            status=Vote.THUMBS_UP, voted_by=self.user)
        self.submission2 = Submission.objects.create(
            artwork=self.artwork2,
            exhibition=self.exhibition,
            submitted_by=self.user)

        self.artwork1 = Artwork.objects.get(id=self.artwork1.id)
        self.artwork2 = Artwork.objects.get(id=self.artwork2.id)

    def test_submitted_artwork_list(self):
        client = Client()
        list_path = reverse('artwork-list')

        # Can see submitted artwork in list
        response = client.get(list_path)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['object_list'].count(), 2)

        # Can see submission URL, not artwork URL
        self.assertEquals(response.context['object_list'][0].get_absolute_url(),
            reverse('submission-view', kwargs={'pk': self.artwork2.shared}))
        self.assertEquals(response.context['object_list'][1].get_absolute_url(),
            reverse('submission-view', kwargs={'pk': self.artwork1.shared}))

        # Can see submissions for both artworks
        self.assertIn('submissions', response.context)
        self.assertIn(self.artwork1.id, response.context['submissions'])
        self.assertIn(self.artwork2.id, response.context['submissions'])

        # Can see vote list for both submissions, with no votes for the
        # unauthenticated user
        self.assertIn('votes', response.context)
        self.assertNotIn(self.submission1.id, response.context['votes'])
        self.assertNotIn(self.submission2.id, response.context['votes'])

        # Login to see user's vote for artwork1
        logged_in = client.login(username=self.get_username(), password=self.get_password())
        self.assertTrue(logged_in)
        response = client.get(list_path)

        self.assertIn('votes', response.context)
        self.assertIn(self.submission1.id, response.context['votes'])
        self.assertNotIn(self.submission2.id, response.context['votes'])


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


class ArtworkCodeViewTests(UserSetUp, TestCase):
    """Artwork view code tests."""

    def test_private_artwork(self):
        
        client = Client()

        # Artwork is private to the author (until submitted)
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        artwork_url = reverse('artwork-code', kwargs={'pk':artwork.id})
        response = client.get(artwork_url)
        login_url = '%s?next=%s' % (reverse('login'), artwork_url)
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)

        # Must login to see it
        response = self.assertLogin(client, artwork_url)
        self.assertEquals(response.get('Content-Disposition'), 'attachment;')
        self.assertEquals(response.context['object'].code, artwork.code)
        self.assertEquals(response.context['object'].title, artwork.title)
        self.assertEquals(response.context['object'].author, artwork.author)

    def test_shared_artwork(self):
        
        client = Client()

        # Shared artwork is public (no login required)
        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', shared=1, author=self.user)
        artwork_url = reverse('artwork-code', kwargs={'pk':artwork.id})

        response = client.get(artwork_url)
        self.assertEquals(response.get('Content-Disposition'), 'attachment;')
        self.assertEquals(response.context['object'].code, artwork.code)
        self.assertEquals(response.context['object'].title, artwork.title)
        self.assertEquals(response.context['object'].author, artwork.author)

    def test_artwork_404(self):
        
        client = Client()
        response = client.get(reverse('artwork-code', kwargs={'pk':1}))
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
        view_url = artwork.get_absolute_url()
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
        artwork = Artwork.objects.create(title='Other User artwork', code='// code goes here', author=otherUser)
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='goes here',
            author=self.staff_user)
        submission = Submission.objects.create(
            artwork=artwork,
            exhibition=exhibition,
            submitted_by=otherUser)
        artwork = Artwork.objects.get(pk=artwork.id)

        delete_url = reverse('artwork-delete', kwargs={'pk':artwork.id})
        response = client.get(delete_url)

        # delete requires login
        login_url = '%s?next=%s' % (reverse('login'), delete_url)
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)
        logged_in = client.login(username=self.get_username(), password=self.get_password())
        self.assertTrue(logged_in)

        # however, we still can't delete the artwork, because we don't own it
        view_url = artwork.get_absolute_url()
        response = client.get(delete_url)
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # nor by post
        response = client.post(delete_url)
        self.assertRedirects(response, view_url, status_code=302, target_status_code=200)

        # Login to ensure the artwork still exists
        response = client.get(view_url)
        self.assertEquals(response.context['object'].artwork.title, artwork.title)


class ArtworkCreateTests(UserSetUp, TestCase):

    def test_create(self):
        client = Client()

        add_path = reverse('artwork-add')
        login_path = '%s?next=%s' % (reverse('login'), add_path)
        list_path = reverse('artwork-list')

        # Ensure no artworks yet
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 0)

        # Create view redirects to login
        response = client.get(add_path)
        self.assertRedirects(response, login_path, status_code=302, target_status_code=200)

        # Post to create - unauthenticated redirects to login
        post_content = {'title': 'My artwork title', 'code': '/* test code */'}
        response = client.post(add_path, post_content)
        self.assertRedirects(response, login_path, status_code=302, target_status_code=200)

        # Login
        response = self.assertLogin(client, add_path)
        self.assertEquals(response.context['object'], '')
        
        # Post an update - succeeds as author (can't assertRedirects; don't know new object id)
        response = client.post(add_path, post_content)

        # Ensure the change was saved
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0].title, post_content['title'])
        self.assertEquals(response.context['object_list'][0].code, post_content['code'])


class ArtworkCloneTests(UserSetUp, TestCase):

    def test_clone(self):
        client = Client()

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', shared=1, author=self.user)

        clone_path = reverse('artwork-clone', kwargs={'pk': artwork.id})
        login_path = '%s?next=%s' % (reverse('login'), clone_path)
        list_path = reverse('artwork-list')

        # Ensure only 1 artwork in the list
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0].title, artwork.title)
        self.assertEquals(response.context['object_list'][0].code, artwork.code)

        # Clone view redirects to login
        response = client.get(clone_path)
        self.assertRedirects(response, login_path, status_code=302, target_status_code=200)

        # Post to create - unauthenticated redirects to login
        post_content = {'code': '/* updated code */', 'title': 'Updated title'}
        response = client.post(clone_path, post_content)
        self.assertRedirects(response, login_path, status_code=302, target_status_code=200)

        # Login
        response = self.assertLogin(client, clone_path)
        self.assertEquals(response.context['object'], '')
        self.assertEquals(
            '%s' % response.context['form'],
            '''<tr><th><label for="id_title">Title:</label></th><td><input id="id_title" maxlength="500" name="title" type="text" value="[Clone] %s" /><input id="id_code" name="code" type="hidden" value="/* Cloned from http://testserver%s */
%s" /></td></tr>'''
            % (artwork.title, reverse('artwork-view', kwargs={'pk': artwork.id}), artwork.code)
        )
        
        # Post an update - succeeds as author (can't assertRedirects; don't know new object id)
        response = client.post(clone_path, post_content)

        # Ensure the change was saved (to logged-in list page)
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 2)
        self.assertEquals(response.context['object_list'][0].title, post_content['title'])
        self.assertEquals(response.context['object_list'][0].code, post_content['code'])
        self.assertEquals(response.context['object_list'][1].title, artwork.title)
        self.assertEquals(response.context['object_list'][1].code, artwork.code)

        # Logout, and ensure only the original artwork is visible (shared
        # setting does not get Cloned)
        client.logout()
        response = client.get(list_path)
        self.assertEquals(response.context['object_list'].count(), 1)
        self.assertEquals(response.context['object_list'][0].title, artwork.title)
        self.assertEquals(response.context['object_list'][0].code, artwork.code)


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

    def test_author_cant_edit_shared_artwork(self):
        
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

        # Post an update - not permitted for shared artwork
        response = client.post(edit_url, {'title': 'My overridden title', 'code': artwork.code})
        self.assertEquals(response.status_code, 403)

        # Ensure the change was not saved
        response = client.get(view_url)
        self.assertEquals(response.context['object'].title, 'Title bar')

    def test_non_author_cant_edit_unshared_artwork(self):
        
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

