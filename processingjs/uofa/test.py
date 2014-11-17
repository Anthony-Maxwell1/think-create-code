from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities    

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from pyvirtualdisplay import Display

import os
import re
import time
from contextlib import contextmanager


class UserSetUp:
    def setUp(self):
        # Create a basic (student) user
        self.password = 'some_password'
        self.user = get_user_model().objects.create(username='student_user')
        self.user.set_password(self.password)
        self.user.save()

        # Create a staff user
        self.staff_password = 'staff_password'
        self.staff_user = get_user_model().objects.create(username='staff_user')
        self.staff_user.is_staff = True
        self.staff_user.set_password(self.staff_password)
        self.staff_user.save()

        # Create a super user
        self.super_password = 'super_password'
        self.super_user = get_user_model().objects.create(username='super_user')
        self.super_user.is_superuser = True
        self.super_user.set_password(self.super_password)
        self.super_user.save()

    def get_username(self, user='default'):
        if user == 'staff':
            return self.staff_user.username
        elif user == 'super':
            return self.super_user.username
        return self.user.username

    def get_password(self, user='default'):
        if user == 'staff':
            return self.staff_password
        elif user == 'super':
            return self.super_password
        return self.password

    def assertLogin(self, client, next_path='', user='default'):
        login_path = reverse('login')
        if next_path:
            login_path = '%s?next=%s' % (login_path, next_path)

        # login client
        logged_in = client.login(username=self.get_username(user), password=self.get_password(user))
        self.assertTrue(logged_in)

        # go to next_path
        return client.get(next_path)


class SeleniumTestCase(UserSetUp, LiveServerTestCase):
    """Run live server integration tests.  Requires running xvfb service."""

    @classmethod
    def setUpClass(cls):
        # /etc/init.d/xfvb running on port 0
        os.environ['DISPLAY'] = ':0'
        os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = '0.0.0.0:8080'

        # enable browser logging
        capabilities = DesiredCapabilities.FIREFOX
        capabilities['loggingPrefs'] = { 'browser':'ALL' }

        cls.selenium = WebDriver(capabilities=capabilities)
        cls.display = Display(visible=0, size=(800, 600))
        cls.display.start()
        super(SeleniumTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        cls.display.stop()
        super(SeleniumTestCase, cls).tearDownClass()

    def get_browser_log(self, level=None):
        '''Return the browser log entries matching the given filters, if given'''
        entries = []
        for entry in self.selenium.get_log('browser'):
            # We only care about errors, not the slew of CSS warnings
            if not level or entry['level'] == level:
                entries.append(entry)
        return entries

    def performLogin(self, user='default'):
        '''Go to the login page, and assert login'''

        login_url = '%s%s' % (self.live_server_url, reverse('login'))
        self.selenium.get(login_url)
        self.assertLogin(user=user)

    def assertLogin(self, next_path = '', user='default'):
        '''Assert that we are at the login page, perform login, and assert success.'''
        self._doLogin(next_path, user)
        if next_path:
            next_url = '%s%s' % (self.live_server_url, next_path)
        else:
            next_url = '%s%s' % (self.live_server_url, '/')
        self.assertEqual(self.selenium.current_url, next_url)
    
    def assertLoginRedirects(self, next_path = '', redirect_path='/', user='default'):
        '''Assert that we are at the login page, perform login, and assert success.'''
        self._doLogin(next_path, user)
        redirect_url = '%s%s' % (self.live_server_url, redirect_path)
        self.assertEqual(self.selenium.current_url, redirect_url)
    
    def _doLogin(self, next_path = '', user='default'):
        '''Assert that we are at the login page, perform login, and assert success.'''

        login_url = '%s%s' % (self.live_server_url, reverse('login'))
        if next_path:
            login_url = '%s?next=%s' % (login_url, next_path)

        self.assertEqual(self.selenium.current_url, login_url)

        if next_path:
            self.assertEqual(self.selenium.find_element_by_name('next').get_attribute('value'), next_path)

        self.selenium.find_element_by_id('id_username').send_keys(self.get_username(user))
        self.selenium.find_element_by_id('id_password').send_keys(self.get_password(user))
        self.selenium.find_element_by_tag_name('button').click()


@contextmanager
def wait_for_page_load(browser):
    '''
    Helper wrapper for Selenium click().
    Usage:
        with wait_for_page_load(browser):
            browser.find_element_by_link_text('my link').click()
    ref: http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html
    '''

    def wait_for(condition_function, wait=3, sleep=0.1):
        start_time = time.time()
        while time.time() < start_time + wait:
            if condition_function():
                return True
            else:
                time.sleep(sleep)
        raise Exception(
            'Timeout waiting for {}'.format(condition_function.__name__)
        )

    old_page = browser.find_element_by_tag_name('html')

    yield

    def page_has_loaded():
        try:
            new_page = browser.find_element_by_tag_name('html')
            return new_page.id != old_page.id
        except NoSuchElementException:
            return False

    wait_for(page_has_loaded)
