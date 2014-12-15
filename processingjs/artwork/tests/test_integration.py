from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
import time

from artwork.models import Artwork
from uofa.test import SeleniumTestCase, wait_for_page_load


class ArtworkListIntegrationTests(SeleniumTestCase):

    def test_public_artwork_listed(self):

        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)

        list_path = reverse('artwork-list')
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            3
        )
        titles = self.selenium.find_elements_by_css_selector('.artwork-title')
        self.assertEqual(
            titles[0].text,
            artwork1.title
        )
        self.assertEqual(
            titles[1].text,
            artwork2.title
        )
        self.assertEqual(
            titles[2].text,
            artwork3.title
        )

        self.assertIsNotNone(
            self.selenium.find_element_by_id('artwork-add')
        )

    def test_user_artwork_listed(self):

        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)

        list_path = reverse('artwork-author-list', kwargs={'author': self.user.id})
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            artwork1.title
        )

        list_path = reverse('artwork-author-list', kwargs={'author': self.staff_user.id})
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            artwork2.title
        )

        list_path = reverse('artwork-author-list', kwargs={'author': self.super_user.id})
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            artwork3.title
        )

    def test_my_artwork_listed(self):

        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)

        list_url = '%s%s' % (self.live_server_url, reverse('artwork-list'))

        self.performLogin(user="student")
        with wait_for_page_load(self.selenium):
            self.selenium.get(list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            artwork1.title
        )

        self.performLogin(user="staff")
        with wait_for_page_load(self.selenium):
            self.selenium.get(list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            artwork2.title
        )

        self.performLogout()
        self.performLogin(user="super")
        with wait_for_page_load(self.selenium):
            self.selenium.get(list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            artwork3.title
        )

    def test_add_artwork_linked(self):

        list_path = reverse('artwork-list')
        self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertIsNotNone(
            self.selenium.find_element_by_id('artwork-add')
        )

    def test_artwork_compile_error(self):

        Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', author=self.user)
        Artwork.objects.create(title='Good test code1', code='// good code!', author=self.user)
        Artwork.objects.create(title='Bad test code2', code='still bad code!', author=self.user)

        list_path = reverse('artwork-list')
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            3
        )

        # We should get 2 errors in the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0]['message'], 'SyntaxError: missing ; before statement')
        self.assertEqual(errors[1]['message'], 'SyntaxError: missing ; before statement')

        # TODO: we're inferring that the 2nd "good" artwork did get rendered,
        # by assuring that the error from the  1st "bad" artwork did not halt
        # processing, since the 3rd bad artwork threw an error too.
        # Not sure how else to test this?


class ArtworkViewIntegrationTests(SeleniumTestCase):

    def test_artwork_view(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)

        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, view_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )


class ArtworkCodeViewIntegrationTests(SeleniumTestCase):

    def test_artwork_code(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)

        code_path = reverse('artwork-code', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, code_path))

        # Selenium wraps the text/plain result in an HTML page for some reason 
        pre_code = self.selenium.find_element_by_tag_name('pre')

        self.assertEqual(
            pre_code.text, artwork.code
        )


class ArtworkRenderViewIntegrationTests(SeleniumTestCase):

    def test_artwork_render(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)

        render_path = reverse('artwork-render', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, render_path))

        script_code = self.selenium.find_element_by_id('script-preview').get_attribute('innerHTML');
        self.assertEqual(
            script_code, artwork.code
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('canvas')),
            1
        )

    def test_artwork_render_compile_error(self):

        artwork = Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', author=self.user)

        render_path = reverse('artwork-render', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, render_path))

        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('canvas')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_id('script-preview')),
            1
        )

        # We should get 1 error in the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['message'], 'SyntaxError: missing ; before statement')


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
        view_path = reverse('artwork-view', kwargs={'pk': 1})
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, view_path))
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

    def test_add_artwork_compile_error(self):

        add_path = reverse('artwork-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form
        self.assertLogin(add_path)

        # login form redirects to add form
        self.selenium.find_element_by_id('id_title').send_keys('bad submission')
        self.selenium.find_element_by_id('id_code').send_keys('bad code!')

        # Draw button catches error, which shows on screen, not in the console
        self.selenium.find_element_by_id('draw').click()
        self.assertEqual(
            self.selenium.find_element_by_id('error').text,
            'missing ; before statement'
        )
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

        # Save button takes you to the view page
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_artwork').click()

        # Wait for iframe to load, and error to appear in console
        time.sleep(5)

        # There should be no error in the console, because the artwork is iframed.
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['message'], 'SyntaxError: missing ; before statement')


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

        # save returns us to the view page
        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, view_path))

        # Wait for iframe to load
        time.sleep(5)

        # ensure edit was saved
        artwork = Artwork.objects.get(pk=artwork.id)
        self.assertEqual(
            artwork.title,
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

        # edit was canceled
        artwork = Artwork.objects.get(pk=artwork.id)
        self.assertEqual(
            artwork.title,
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

