from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from artwork.models import Artwork, ArtworkForm
from gallery.tests import UserSetUp, SeleniumTestCase


class ArtworkTests(TestCase):
    """Artwork model tests."""

    def test_str(self):
        
        artwork = Artwork(title='Empty code', code='// code goes here')

        self.assertEquals(
            str(artwork),
            'Empty code'
        )


class ArtworkListTests(UserSetUp, TestCase):
    """Artwork list view tests."""

    def test_artwork_in_the_context(self):
        
        client = Client()
        response = client.get('/')

        self.assertEquals(list(response.context['object_list']), [])

        Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        response = client.get('/')
        self.assertEquals(response.context['object_list'].count(), 1)


class ArtworkViewTests(UserSetUp, TestCase):
    """Artwork view tests."""

    def test_artwork_in_the_context(self):
        
        client = Client()

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        response = client.get(reverse('artwork-view', kwargs={'pk':artwork.id}))
        self.assertEquals(response.context['object'].title, artwork.title)
        self.assertEquals(response.context['object'].code, artwork.code)


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
        logged_in = client.login(username=self.username, password=self.password)
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
        logged_in = client.login(username=self.username, password=self.password)
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
        logged_in = client.login(username=self.username, password=self.password)
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
        logged_in = client.login(username=self.username, password=self.password)
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


class ArtworkModelFormTests(UserSetUp, TestCase):
    """model.ArtworkForm tests."""

    def test_login(self):
        form_data = {
            'title': 'Title bar',
            'code': '// code goes here',
        }

        # Form requires logged-in user
        form = ArtworkForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertRaises(IntegrityError, form.save)

    def test_validation(self):

        form_data = {
            'title': 'Title bar',
            'code': '// code goes here'
        }

        form = ArtworkForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.instance.title, form_data['title'])
        self.assertEqual(form.instance.code, form_data['code'])

        # Have to set the author before we can save
        form.instance.author_id = self.user.id
        form.save()

        self.assertEqual(
            Artwork.objects.get(id=form.instance.id).title,
            'Title bar'
        )

    def test_invalidation(self):
        form_data = {
            'title': 'Title bar',
        }

        form = ArtworkForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.instance.title, form_data['title'])

        self.assertRaises(ValueError, form.save)


class ArtworkListIntegrationTests(SeleniumTestCase):

    def test_artwork_listed(self):

        Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)

        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id('list-artwork-add')
        )

    def test_add_artwork_linked(self):

        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.assertIsNotNone(
            self.selenium.find_element_by_id('list-artwork-add')
        )


class ArtworkAddIntegrationTests(SeleniumTestCase):

    def test_add_artwork(self):

        add_path = reverse('artwork-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form
        self.assertLogin(add_path)

        # login form redirects to add form
        self.selenium.find_element_by_id('id_title').send_keys('test submission')
        self.selenium.find_element_by_id('id_code').send_keys('// code goes here')

        self.selenium.find_element_by_id('save_artwork').click()

        # add action redirects to root url
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, '/'))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )

    def test_add_artwork_cancel(self):

        add_path = reverse('artwork-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form
        self.assertLogin(add_path)

        # login form redirects to add form
        self.selenium.find_element_by_id('id_title').send_keys('do not submit')
        self.selenium.find_element_by_id('id_code').send_keys('// code goes here')

        self.selenium.find_element_by_id('save_cancel').click()

        # cancel action redirects to root url
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, '/'))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )


class ArtworkEditIntegrationTests(SeleniumTestCase):

    def test_edit_artwork(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)

        edit_path = reverse('artwork-edit', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))

        # edit redirects to login form
        self.assertLogin(edit_path)

        # Update the title text
        self.selenium.find_element_by_id('id_title').clear()
        self.selenium.find_element_by_id('id_title').send_keys('updated title')

        # Click Save
        self.selenium.find_element_by_id('save_artwork').click()

        # save returns us to the home page
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, '/'))

        # view the work to ensure edit was saved
        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, view_path))
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            'updated title'
        )

    def test_edit_artwork_cancel(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)

        edit_path = reverse('artwork-edit', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))

        # edit redirects to login form
        self.assertLogin(edit_path)

        # Update the title text
        self.selenium.find_element_by_id('id_title').clear()
        self.selenium.find_element_by_id('id_title').send_keys('updated title')

        # Click cancel
        self.selenium.find_element_by_id('save_cancel').click()

        # Cancel returns us to the home page
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, '/'))

        # view the work to ensure edit was canceled
        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, view_path))
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            'Title bar'
        )

    def test_not_author_edit(self):
        # 1. Create a second user
        otherUser = get_user_model().objects.create(username='other')

        # 2. Create an artwork authored by the second user
        artwork = Artwork.objects.create(title='Other User artwork', code='// code goes here', author=otherUser)

        # 3. Login
        self.performLogin()

        # 3. Try to edit artwork via GET request
        edit_url = '%s%s' % (self.live_server_url, reverse('artwork-edit', kwargs={'pk': artwork.id}))
        self.selenium.get(edit_url)
        
        # 4. Ensure we're redirected back to view
        view_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': artwork.id}))
        self.assertEqual(self.selenium.current_url, view_url)


class ArtworkDeleteIntegrationTests(SeleniumTestCase):

    def test_delete_artwork(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        delete_path = reverse('artwork-delete', kwargs={'pk':artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, delete_path))

        # delete redirects to login form
        self.assertLogin(delete_path)

        # login form redirects to delete form
        self.selenium.find_element_by_id('artwork_delete').click()

        # delete action redirects to root url
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, '/'))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        
    def test_delete_artwork_cancel(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        delete_path = reverse('artwork-delete', kwargs={'pk':artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, delete_path))

        # delete redirects to login form
        self.assertLogin(delete_path)

        # login form redirects to delete form
        self.selenium.find_element_by_id('artwork_do_not_delete').click()

        # delete action redirects to root url
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, '/'))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )

    def test_not_author_delete(self):
        # 1. Create a second user
        otherUser = get_user_model().objects.create(username='other')

        # 2. Create an artwork authored by the second user
        artwork = Artwork.objects.create(title='Other User artwork', code='// code goes here', author=otherUser)

        # 3. Login
        self.performLogin()

        # 3. Try to delete artwork via GET request
        delete_url = '%s%s' % (self.live_server_url, reverse('artwork-delete', kwargs={'pk': artwork.id}))
        self.selenium.get(delete_url)
        
        # 4. Ensure we're redirected back to view
        view_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': artwork.id}))
        self.assertEqual(self.selenium.current_url, view_url)
