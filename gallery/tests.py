from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from selenium.webdriver.firefox.webdriver import WebDriver
from pyvirtualdisplay import Display

import os, re


class UserSetUp:
    def setUp(self):
        self.username = 'some_user'
        self.password = 'some_password'
        self.user = get_user_model().objects.create(username=self.username)
        self.user.set_password(self.password)
        self.user.save()


class SeleniumTestCase(UserSetUp, LiveServerTestCase):
    """Run live server integration tests.  Requires running xvfb service."""

    @classmethod
    def setUpClass(cls):
        # /etc/init.d/xfvb running on port 0
        os.environ['DISPLAY'] = ':0'
        os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = '0.0.0.0:8080'
        cls.selenium = WebDriver()
        cls.display = Display(visible=0, size=(800, 600))
        cls.display.start()
        super(SeleniumTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        cls.display.stop()
        super(SeleniumTestCase, cls).tearDownClass()

    def performLogin(self):
        '''Go to the login page, and assert login'''

        login_url = '%s%s' % (self.live_server_url, reverse('login'))
        self.selenium.get(login_url)
        self.assertLogin()

    def assertLogin(self, next_path = ''):
        '''Assert that we are at the login page, perform login, and assert success.'''

        login_url = '%s%s' % (self.live_server_url, reverse('login'))
        if next_path:
            login_url = '%s?next=%s' % (login_url, next_path)
            next_url = '%s%s' % (self.live_server_url, next_path)
        else:
            next_url = '%s%s' % (self.live_server_url, '/')

        self.assertEqual(self.selenium.current_url, login_url)

        if next_path:
            self.assertEqual(self.selenium.find_element_by_name('next').get_attribute('value'), next_path)

        self.selenium.find_element_by_id('id_username').send_keys(self.username)
        self.selenium.find_element_by_id('id_password').send_keys(self.password)
        self.selenium.find_element_by_tag_name('button').click()

        self.assertEqual(self.selenium.current_url, next_url)



class GalleryAuthIntegrationTests(SeleniumTestCase):

    def test_login(self):
        self.performLogin()


    def test_login_fail(self):
        login_url = '%s%s' % (self.live_server_url, reverse('login'))
        self.selenium.get(login_url)
        self.assertEqual(self.selenium.current_url, login_url)

        self.selenium.find_element_by_id('id_username').send_keys(self.username)
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
