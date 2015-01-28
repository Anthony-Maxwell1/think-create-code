from django.core.urlresolvers import reverse
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from django.contrib.auth import get_user_model
import time

from artwork.models import Artwork
from uofa.test import SeleniumTestCase, NoHTML5SeleniumTestCase, wait_for_page_load


class ArtworkListIntegrationTests(SeleniumTestCase):

    def test_private_artwork_listed(self):

        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)

        # Public can't see any artworks
        list_path = reverse('artwork-list')
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )

        # Can login to see my artwork, but no one else's
        self.performLogin()
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

    def test_shared_artwork_listed(self):

        list_path = reverse('artwork-list')

        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', shared=1, author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', shared=4, author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', shared=78, author=self.super_user)

        # Shared artwork is visible to the public
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            3
        )
        titles = self.selenium.find_elements_by_css_selector('.artwork-title')
        self.assertEqual(
            titles[0].text,
            artwork3.title
        )
        self.assertEqual(
            titles[1].text,
            artwork2.title
        )
        self.assertEqual(
            titles[2].text,
            artwork1.title
        )

        self.assertIsNotNone(
            self.selenium.find_element_by_id('artwork-add')
        )

        # Shared artwork + own private artwork is visible to logged-in users
        artwork4 = Artwork.objects.create(title='Artwork 4', code='// code goes here', shared=1, author=self.user)
        self.performLogin()
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            4
        )
        titles = self.selenium.find_elements_by_css_selector('.artwork-title')
        self.assertEqual(
            titles[0].text,
            artwork4.title
        )
        self.assertEqual(
            titles[1].text,
            artwork3.title
        )
        self.assertEqual(
            titles[2].text,
            artwork2.title
        )
        self.assertEqual(
            titles[3].text,
            artwork1.title
        )

    def test_private_user_artwork_listed(self):

        # private artwork is not visible to public
        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)

        list_path = reverse('artwork-author-list', kwargs={'author': self.user.id})
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )

        list_path = reverse('artwork-author-list', kwargs={'author': self.staff_user.id})
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )

        list_path = reverse('artwork-author-list', kwargs={'author': self.super_user.id})
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )

    def test_shared_user_artwork_listed(self):

        # Shared artwork is visible to public
        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', shared=1, author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', shared=1, author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', shared=1, author=self.super_user)

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

    def test_studio_artwork_listed(self):

        artwork1 = Artwork.objects.create(title='Artwork 1', code='// code goes here', author=self.user)
        artwork2 = Artwork.objects.create(title='Artwork 2', code='// code goes here', author=self.staff_user)
        artwork3 = Artwork.objects.create(title='Artwork 3', code='// code goes here', author=self.super_user)

        # My Studio URL redirects to login page for unauthenticated users
        studio_path = reverse('artwork-studio')
        studio_url = '%s%s' % (self.live_server_url, studio_path)
        with wait_for_page_load(self.selenium):
            self.selenium.get(studio_url)
        login_url = '%s%s?next=%s' % (self.live_server_url, reverse('login'), studio_path)
        self.assertEqual(self.selenium.current_url, login_url)

        # My Studio URL redirects to author list for authenticated users
        
        # Student login
        self.performLogin(user='student')
        with wait_for_page_load(self.selenium):
            self.selenium.get(studio_url)
        list_path = reverse('artwork-author-list', kwargs={'author': self.user.id, 'shared': 0})
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            artwork1.title
        )

        # Staff login
        self.performLogin(user='staff')
        with wait_for_page_load(self.selenium):
            self.selenium.get(studio_url)
        list_path = reverse('artwork-author-list', kwargs={'author': self.staff_user.id, 'shared': 0})
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.artwork-title').text,
            artwork2.title
        )

        # Super login
        self.performLogin(user='super')
        with wait_for_page_load(self.selenium):
            self.selenium.get(studio_url)
        list_path = reverse('artwork-author-list', kwargs={'author': self.super_user.id, 'shared': 0})
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))
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

        # Author list shows only shared artwork
        list_url = '%s%s' % (self.live_server_url, reverse('artwork-author-list', kwargs={'author':self.user.id}))

        # Student user
        self.performLogin(user="student")
        with wait_for_page_load(self.selenium):
            self.selenium.get(list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        artwork1.shared = 1
        artwork1.save()
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

        # Staff user
        self.performLogin(user="staff")
        list_url = '%s%s' % (self.live_server_url, reverse('artwork-author-list', kwargs={'author':self.staff_user.id}))
        with wait_for_page_load(self.selenium):
            self.selenium.get(list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        artwork2.shared = 1
        artwork2.save()
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

        # Super user
        self.performLogout()
        self.performLogin(user="super")
        list_url = '%s%s' % (self.live_server_url, reverse('artwork-author-list', kwargs={'author':self.super_user.id}))
        with wait_for_page_load(self.selenium):
            self.selenium.get(list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        artwork3.shared = 1
        artwork3.save()
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

class ArtworkViewIntegrationTests(SeleniumTestCase):

    def test_own_artwork_view(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        view_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': artwork.id}))

        # Public cannot see unshared artwork
        self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        error_403 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_403.text, '403 Forbidden'
        )

        # Owner can see it
        self.performLogin()
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )

        # Staff cannot
        self.performLogout()
        self.performLogin(user="staff")
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        error_403 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_403.text, '403 Forbidden'
        )

        # Super cannot
        self.performLogout()
        self.performLogin(user="super")
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        error_403 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_403.text, '403 Forbidden'
        )

    def test_shared_artwork_view(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', shared=3, author=self.user)
        view_url = '%s%s' % (self.live_server_url, reverse('artwork-view', kwargs={'pk': artwork.id}))

        # Public can see shared artwork
        self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )

        # Owner can see it
        self.performLogin()
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )

        # Staff can see it
        self.performLogout()
        self.performLogin(user="staff")
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )

        # Super can see it
        self.performLogout()
        self.performLogin(user="super")
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )

    def test_private_artwork_links(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)

        # Public can't see artwork
        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})
        view_url = '%s%s' % (self.live_server_url, view_path)

        self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        # and no edit links
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('EDIT')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('DELETE')
        )

        # Owner can see it
        self.performLogin()
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        # and edit links
        self.assertIsNotNone(
            self.selenium.find_element_by_link_text, ('EDIT')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_link_text, ('DELETE')
        )
        # and clicking on them redirects to expected page
        self.selenium.find_element_by_link_text('EDIT').click()
        self.assertEqual(self.selenium.current_url, 
            '%s%s' % (self.live_server_url, reverse('artwork-edit', kwargs={'pk': artwork.id})))
        
        self.selenium.get(view_url)
        self.selenium.find_element_by_link_text('DELETE').click()
        self.assertEqual(self.selenium.current_url, 
            '%s%s' % (self.live_server_url, reverse('artwork-delete', kwargs={'pk': artwork.id})))


        # Staff can't see it
        self.performLogout()
        self.performLogin(user="staff")
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        # and no edit links
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('EDIT')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('DELETE')
        )

        # Super can't see it
        self.performLogout()
        self.performLogin(user="super")
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        # and no edit links
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('EDIT')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('DELETE')
        )

    def test_shared_artwork_links(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', shared=3, author=self.user)

        # Public can see shared artwork
        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})
        view_url = '%s%s' % (self.live_server_url, view_path)

        self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        # but no edit links
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('EDIT')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('DELETE')
        )

        # Owner can see it
        self.performLogin()
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        # and edit links
        self.assertIsNotNone(
            self.selenium.find_element_by_link_text, ('EDIT')
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_link_text, ('DELETE')
        )
        # and clicking on them redirects to expected page
        self.selenium.find_element_by_link_text('EDIT').click()
        self.assertEqual(self.selenium.current_url, 
            '%s%s' % (self.live_server_url, reverse('artwork-edit', kwargs={'pk': artwork.id})))
        
        self.selenium.get(view_url)
        self.selenium.find_element_by_link_text('DELETE').click()
        self.assertEqual(self.selenium.current_url, 
            '%s%s' % (self.live_server_url, reverse('artwork-delete', kwargs={'pk': artwork.id})))


        # Staff can see it
        self.performLogout()
        self.performLogin(user="staff")
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        # but no edit links
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('EDIT')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('DELETE')
        )

        # Super can see it
        self.performLogout()
        self.performLogin(user="staff")
        with wait_for_page_load(self.selenium):
            self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('EDIT')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('DELETE')
        )


class ArtworkCodeViewIntegrationTests(SeleniumTestCase):

    def test_own_artwork_code(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)

        code_path = reverse('artwork-code', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, code_path))

        # Public cannot see unshared code
        code_path = reverse('artwork-code', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, code_path))
        error_403 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_403.text, '403 Forbidden'
        )

        # Owner can see it
        self.performLogin()
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, code_path))
        # Selenium wraps the text/plain result in an HTML page for some reason 
        pre_code = self.selenium.find_element_by_tag_name('pre')
        self.assertEqual(
            pre_code.text, artwork.code
        )

        # Staff cannot
        self.performLogout()
        self.performLogin(user="staff")
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, code_path))
        error_403 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_403.text, '403 Forbidden'
        )

        # Super cannot
        self.performLogout()
        self.performLogin(user="staff")
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, code_path))
        error_403 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_403.text, '403 Forbidden'
        )

    def test_shared_artwork_code(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', shared=42, author=self.user)

        code_path = reverse('artwork-code', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, code_path))

        # Public can see shared code
        code_path = reverse('artwork-code', kwargs={'pk': artwork.id})
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, code_path))
        pre_code = self.selenium.find_element_by_tag_name('pre')
        self.assertEqual(
            pre_code.text, artwork.code
        )

        # Owner can see it
        self.performLogin()
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, code_path))
        pre_code = self.selenium.find_element_by_tag_name('pre')
        self.assertEqual(
            pre_code.text, artwork.code
        )

        # Staff can
        self.performLogout()
        self.performLogin(user="staff")
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, code_path))
        pre_code = self.selenium.find_element_by_tag_name('pre')
        self.assertEqual(
            pre_code.text, artwork.code
        )

        # Super can
        self.performLogout()
        self.performLogin(user="staff")
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, code_path))
        pre_code = self.selenium.find_element_by_tag_name('pre')
        self.assertEqual(
            pre_code.text, artwork.code
        )


class ArtworkRenderViewIntegrationTests(SeleniumTestCase):

    def test_artwork_render(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)

        render_path = reverse('artwork-render', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, render_path))

        # Render page must be iframed to actually render code

        # Should show not-rendered div
        self.assertEqual(self.get_style_property('artwork-not-rendered', 'display'), 'block')

        # .. instead of the rendered div
        self.assertEqual(self.get_style_property('artwork-rendered', 'display'), 'none')

        script_code = self.selenium.find_element_by_id('script-preview').get_attribute('innerHTML');
        self.assertEqual(
            script_code, ''
        )


class ArtworkAddIntegrationTests(SeleniumTestCase):

    def test_add_artwork(self):

        add_path = reverse('artwork-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form
        self.assertLogin(add_path)

        # login form redirects to add form
        self.selenium.find_element_by_id('id_title').send_keys('test submission')
        self.selenium.find_element_by_css_selector('.ace_text-input').send_keys('// code goes here')

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
        self.selenium.find_element_by_css_selector('.ace_text-input').send_keys('// code goes here')

        # No more 'cancel' link on Add Artwork page
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('save_cancel')
        )

        # But if we go to the list url, our artwork is not there.
        list_path = reverse('artwork-list')
        self.selenium.get('%s%s' % (self.live_server_url, list_path))
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

        # Cancel returns us to the view page
        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, view_path))

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

    def test_edit_artwork_code(self):

        '''Ensure that the code editor widget communicates changes ok.'''

        title = 'Title bar'
        code = '// code goes here'
        artwork = Artwork.objects.create(title=title, code=code, author=self.user)

        edit_path = reverse('artwork-edit', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))

        # edit redirects to login form
        self.assertLogin(edit_path)

        # Update the title text 
        new_code = ['''void setup() { size(640, 360); }\n''',
                    '''void draw() { background(0); }''',]

        textarea = self.selenium.find_element_by_css_selector('.ace_text-input')
        textarea.click()
        textarea.send_keys(Keys.CONTROL, 'a') # select all
        textarea.send_keys(Keys.CONTROL, 'x') # delete

        # Wait for editor to load
        #time.sleep(5)

        # Editor will handle indenting and ending braces
        textarea.send_keys(new_code[0])
        textarea.send_keys(new_code[1])

        # form POSTs replace newlines with CRLF, so we need to too.
        new_code = ''.join(new_code)
        new_code = new_code.replace('\n', '\r\n')

        # Click Save
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_artwork').click()

        # save returns us to the view page
        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, view_path))

        # ensure edit was saved
        artwork = Artwork.objects.get(pk=artwork.id)
        self.assertEqual(
            artwork.title,
            title
        )
        self.assertEqual(
            artwork.code,
            new_code
        )


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
            1,
            self.selenium.page_source
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


class ArtworkRender_NoHTML5Iframe_IntegrationTests(NoHTML5SeleniumTestCase):
    '''Tests the artwork rendering in a browser that does not support HTML5 iframe sandbox'''

    def test_artwork_render_compile_error(self):

        artwork = Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', shared=1, author=self.user)

        render_path = reverse('artwork-render', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, render_path))

        # Render page must be iframed to do its job
        # Should show not-rendered div
        self.assertEqual(self.get_style_property('artwork-not-rendered', 'display'), 'block')

        # .. instead of the rendered div
        self.assertEqual(self.get_style_property('artwork-rendered', 'display'), 'none')

        script_code = self.selenium.find_element_by_id('script-preview').get_attribute('innerHTML');
        self.assertEqual(
            script_code, ''
        )

        # We should get no errors in the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

    def test_view_artwork_compile_error(self):

        artwork = Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', shared=1, author=self.user)

        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, view_path))

        # We should get no errors in the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

        # We should be able to see the HTML5 support warning text
        upgradeBrowser = self.selenium.find_element_by_css_selector('.artwork h4')
        self.assertEqual(
            upgradeBrowser.text,
            'Please upgrade your browser'
        )

    def test_artwork_list_compile_error(self):

        Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', shared=1, author=self.user)
        Artwork.objects.create(title='Good test code1', code='// good code!', shared=1, author=self.user)
        Artwork.objects.create(title='Bad test code2', code='still bad code!', shared=1, author=self.user)

        list_path = reverse('artwork-list')
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            3
        )

        # We should get no errors in the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

        # We should be able to see the HTML5 support warning text
        upgradeBrowser = self.selenium.find_elements_by_css_selector('.artwork h4')
        self.assertEqual(len(upgradeBrowser), 3);
        self.assertEqual(
            upgradeBrowser[0].text,
            'Please upgrade your browser'
        )

    def test_add_artwork_compile_error(self):

        add_path = reverse('artwork-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form
        self.assertLogin(add_path)

        # Automatic redraw enabled
        self.assertTrue(self.selenium.find_element_by_id('autoupdate').is_selected())

        self.selenium.find_element_by_id('id_title').send_keys('bad submission')
        self.selenium.find_element_by_css_selector('.ace_text-input').send_keys('bad code makes jack something something;')

        self.assertEqual(
            self.selenium.find_element_by_id('error').text,
            'missing ; before statement'
        )

        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)


class ArtworkRender_HTML5Iframe_IntegrationTests(SeleniumTestCase):
    '''Tests the artwork rendering in a browser that does support HTML5 iframe sandbox'''

    def test_artwork_render_compile_error(self):

        artwork = Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', shared=1, author=self.user)

        render_path = reverse('artwork-render', kwargs={'pk': artwork.id})
        self.selenium.get('%s%s' % (self.live_server_url, render_path))

        # Render page must be iframed to do its job
        # Should show not-rendered div
        self.assertEqual(self.get_style_property('artwork-not-rendered', 'display'), 'block')

        # .. instead of the rendered div
        self.assertEqual(self.get_style_property('artwork-rendered', 'display'), 'none')

        script_code = self.selenium.find_element_by_id('script-preview').get_attribute('innerHTML');
        self.assertEqual(
            script_code, ''
        )

        # We should get no errors in the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)

    def test_artwork_view_compile_error(self):

        artwork = Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', shared=1, author=self.user)

        view_path = reverse('artwork-view', kwargs={'pk': artwork.id})
        with wait_for_page_load(self.selenium):
            self.selenium.get('%s%s' % (self.live_server_url, view_path))

        # HTML5 attributes should be detectable via javascript
        self.assertTrue(self.selenium.execute_script('return Modernizr.sandbox'))

        # We should get 1 error in the logs
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['message'], 'SyntaxError: missing ; before statement')

    def test_artwork_list_compile_error(self):

        Artwork.objects.create(title='Bad test code1', code='bad code! bad!;', shared=1, author=self.user)
        Artwork.objects.create(title='Good test code1', code='// good code!', shared=1, author=self.user)
        Artwork.objects.create(title='Bad test code2', code='still bad code!', shared=1, author=self.user)

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

        # n.b: we're inferring that the 2nd "good" artwork did get rendered,
        # by assuring that the error from the  1st "bad" artwork did not halt
        # processing, since the 3rd bad artwork threw an error too.
        # Not sure how else to test this?

    def test_add_artwork_compile_error(self):

        add_path = reverse('artwork-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form
        self.assertLogin(add_path)

        # Automatic redraw enabled
        self.assertTrue(self.selenium.find_element_by_id('autoupdate').is_selected())

        self.selenium.find_element_by_id('id_title').send_keys('bad submission')
        self.selenium.find_element_by_css_selector('.ace_text-input').send_keys('bad code!')

        self.assertEqual(
            self.selenium.find_element_by_id('error').text,
            'missing ; before statement'
        )
        errors = self.get_browser_log(level=u'SEVERE')
        self.assertEqual(len(errors), 0)
