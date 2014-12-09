import re
from django.core.urlresolvers import reverse

from uofa.test import SeleniumTestCase
from selenium.common.exceptions import NoSuchElementException


class GalleryAuthIntegrationTests(SeleniumTestCase):
    '''Test login, logout'''

    def test_login(self):
        self.performLogin()

    def test_login_fail(self):
        login_url = '%s%s' % (self.live_server_url, reverse('login'))
        self.selenium.get(login_url)
        self.assertEqual(self.selenium.current_url, login_url)

        self.selenium.find_element_by_id('id_username').send_keys(self.get_username())
        self.selenium.find_element_by_id('id_password').send_keys('notavalid password')
        self.selenium.find_element_by_tag_name('button').click()

        # still on login page..
        self.assertEqual(self.selenium.current_url, login_url)

        # ..showing error
        login_error = re.compile(r'Your username and password didn\'t match. Please try again\.')
        self.assertRegexpMatches(self.selenium.page_source, login_error)

    def test_logout(self):

        # 1. login
        self.performLogin()

        # 2. visit "add artwork" page, and ensure we get there
        add_url = '%s%s' % (self.live_server_url, reverse('artwork-add'))
        self.selenium.get(add_url)
        self.assertEqual(self.selenium.current_url, add_url)

        # 3. logout, and check page
        logout_url = '%s%s' % (self.live_server_url, reverse('logout'))
        self.selenium.get(logout_url)
        self.assertEqual(self.selenium.current_url, logout_url)

        # 4. re-visit "add artwork", and ensure we got sent back to login
        self.selenium.get(add_url)
        self.assertEqual(self.selenium.current_url, '%s%s?next=%s' % (self.live_server_url, reverse('login'), reverse('artwork-add')))

    def test_public_nav_links(self):
        base_url = self.live_server_url
        self.selenium.get(base_url)

        # My Studio
        link = self.selenium.find_element_by_link_text('My Studio')
        login_url = '%s%s?next=%s' % (self.live_server_url, reverse('login'), reverse('home'))
        self.assertEqual(
            link.get_attribute('href'),
            login_url
        )

        # Exhibitions
        link = self.selenium.find_element_by_link_text('Exhibitions')
        exhibitions_url = '%s%s' % (self.live_server_url, reverse('exhibition-list'))
        self.assertEqual(
            link.get_attribute('href'),
            exhibitions_url
        )

        # Sign in
        link = self.selenium.find_element_by_id('nav-signin')
        login_url = '%s%s?next=%s' % (self.live_server_url, reverse('login'), reverse('home'))
        self.assertEqual(
            link.get_attribute('href'),
            login_url
        )

        # No sign out
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('nav-signout')
        )

    def test_user_nav_links(self):
        self.performLogin()

        # My Studio
        link = self.selenium.find_element_by_link_text('My Studio')
        home_url = '%s%s' % (self.live_server_url, reverse('home'))
        self.assertEqual(
            link.get_attribute('href'),
            home_url
        )

        # Exhibitions
        link = self.selenium.find_element_by_link_text('Exhibitions')
        exhibitions_url = '%s%s' % (self.live_server_url, reverse('exhibition-list'))
        self.assertEqual(
            link.get_attribute('href'),
            exhibitions_url
        )

        # No sign out
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('nav-signout')
        )

        # No Sign in
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('nav-signin')
        )


class GalleryHomePageIntegrationTests(SeleniumTestCase):
    '''Test the default (home) page'''

    def test_home(self):
        base_url = self.live_server_url
        home_url = '%s%s' % (self.live_server_url, reverse('home'))
        self.selenium.get(base_url)
        self.assertEqual(self.selenium.current_url, home_url)

        # home page is the exhibition list
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('#artwork-list-content')),
            1
        )
