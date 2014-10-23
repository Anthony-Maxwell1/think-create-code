from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from artwork.models import Artwork
from gallery.tests import SeleniumTestCase, wait_for_page_load


class ArtworkListIntegrationTests(SeleniumTestCase):

    def test_artwork_listed(self):

        Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)

        list_path = reverse('artwork-list')
        self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id('list-add-button')
        )

    def test_add_artwork_linked(self):

        list_path = reverse('artwork-list')
        self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertIsNotNone(
            self.selenium.find_element_by_id('list-add-button')
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

        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_artwork').click()

        # add action redirects to list url
        list_path = reverse('artwork-list')
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))
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

        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_cancel').click()

        # cancel action redirects to list url
        list_path = reverse('artwork-list')
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))
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
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_artwork').click()

        # save returns us to the list page
        list_path = reverse('artwork-list')
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))

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
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_cancel').click()

        # Cancel returns us to the list page
        list_path = reverse('artwork-list')
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))

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
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('artwork_delete').click()

        # delete action redirects to list url
        list_path = reverse('artwork-list')
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))
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
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('artwork_do_not_delete').click()

        # delete action redirects to list url
        list_path = reverse('artwork-list')
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))
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

