from django.test import LiveServerTestCase
from django.test.runner import DiscoverRunner
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils.importlib import import_module
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities    

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import NoSuchElementException
from pyvirtualdisplay import Display

import os
import re
import sys
import time
import urllib
from contextlib import contextmanager


class ExcludeAppsTestSuiteRunner(DiscoverRunner):
    EXCLUDED_APPS = getattr(settings, 'TEST_EXCLUDE', [])

    def __init__(self, *args, **kwargs):
        settings.TESTING = True
        super(ExcludeAppsTestSuiteRunner, self).__init__(*args, **kwargs)
    
    def build_suite(self, *args, **kwargs):
        suite = super(ExcludeAppsTestSuiteRunner, self).build_suite(*args, **kwargs)
        if not args[0] and not getattr(settings, 'RUN_ALL_TESTS', False):
            tests = []
            for case in suite:
                pkg = case.__class__.__module__.split('.')[0]
                if pkg not in self.EXCLUDED_APPS:
                    tests.append(case)
            suite._tests = tests 
        return suite
    

class UserSetUp(object):
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
        self.super_user.is_staff = True
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

    def assertLogin(self, client, next_path='', user='default', login='login'):
        login_path = reverse(login)
        if next_path:
            login_path = '%s?next=%s' % (login_path, next_path)

        # login client
        logged_in = client.login(username=self.get_username(user), password=self.get_password(user))
        self.assertTrue(logged_in)

        # go to next_path
        return client.get(next_path)


class InactiveUserSetUp(UserSetUp):

    def activateUser(self, active=True):
        self.inactive_user.is_active = active
        self.inactive_user.save()

    def get_username(self, user='default'):
        if user == 'inactive':
            return self.inactive_user.username
        return super(InactiveUserSetUp, self).get_username(user)

    def get_password(self, user='default'):
        if user == 'inactive':
            return self.inactive_password
        return super(InactiveUserSetUp, self).get_password(user)

    def setUp(self):
        super(InactiveUserSetUp, self).setUp()

        # Create an inactive (student) user
        self.inactive_password = 'inactive_password'
        self.inactive_user = get_user_model().objects.create(username='inactive_user')
        self.inactive_user.set_password(self.inactive_password)
        self.inactive_user.is_active = False
        self.inactive_user.save()

    def assertLogin(self, *args, **kwargs):
        '''Have to activate the inactive user so it can login'''
        inactiveUser = False
        if 'user' in kwargs:
            if kwargs['user'] == 'inactive':
                inactiveUser = True

        if inactiveUser:
            self.activateUser()

        response = super(InactiveUserSetUp, self).assertLogin(*args, **kwargs)

        if inactiveUser:
            self.activateUser(False)
        return response

    def performLogin(self, *args, **kwargs):
        '''Have to activate the inactive user so it can login'''
        inactiveUser = False
        if 'user' in kwargs:
            if kwargs['user'] == 'inactive':
                inactiveUser = True

        if inactiveUser:
            self.activateUser()

        response = super(InactiveUserSetUp, self).performLogin(*args, **kwargs)

        if inactiveUser:
            self.activateUser(False)
        return response


class TestOverrideSettings(object):

    def tearDown(self):
        super(TestOverrideSettings, self).tearDown()
        # reload urlconf without overrides
        self.reload_urlconf()

    def reload_urlconf(self):

        if settings.ROOT_URLCONF in sys.modules:
            reload(sys.modules[settings.ROOT_URLCONF])

        for app in settings.INSTALLED_APPS:
            try:
                module = import_module('%s.urls' % app)
                reload(module)
            except ImportError:
                pass # ignore

        # Need to reload all app urls
        #reload('django_adelaidex.lti.urls')

        return import_module(settings.ROOT_URLCONF)


class SeleniumTestCase(UserSetUp, LiveServerTestCase):
    """Run live server integration tests.  Requires running xvfb service."""

    @classmethod
    def getWebDriver(cls, **kwargs):
        # enable browser logging
        capabilities = DesiredCapabilities.FIREFOX
        capabilities['loggingPrefs'] = { 'browser':'ALL' }
        return  WebDriver(capabilities=capabilities, **kwargs)

    @classmethod
    def setUpClass(cls):
        # /etc/init.d/xfvb running on port 0
        os.environ['DISPLAY'] = ':0'
        os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = '0.0.0.0:8080'

        cls.selenium = cls.getWebDriver()

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

    def get_style_property(self, id, propName):
        '''Return the requested style property for the given element.'''
        return self.selenium.execute_script(
            "var elem = document.getElementById('%s');"
            "if (elem) {"
            "   var style = window.getComputedStyle(elem);"
            "   return style.getPropertyValue('%s');"
            "} else { return null; }"
            % (id, propName)
        )

    def performLogin(self, user='default', login='login'):
        '''Go to the login page, and assert login'''

        login_url = '%s%s' % (self.live_server_url, reverse(login))
        self.selenium.get(login_url)
        self.assertLogin(user=user, login=login)

    def performLogout(self):
        '''Go to the logout page'''

        logout_url = '%s%s' % (self.live_server_url, reverse('logout'))
        self.selenium.get(logout_url)

    def assertLogin(self, next_path = '', user='default', login='login'):
        '''Assert that we are at the login page, perform login, and assert success.'''
        self._doLogin(next_path, user, login)
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
    
    def _doLogin(self, next_path = '', user='default', login='login'):
        '''Assert that we are at the login page, perform login, and assert success.'''

        login_url = '%s%s' % (self.live_server_url, reverse(login))
        if next_path:
            # Encode the few characters that django seems to care about
            enc_next_path = next_path.replace('?', '%3F')
            enc_next_path = enc_next_path.replace('=', '%3D')
            login_url = '%s?next=%s' % (login_url, enc_next_path)

        self.assertEqual(self.selenium.current_url, login_url)

        if next_path:
            self.assertEqual(
                self.selenium.find_element_by_name('next').get_attribute('value'),
                urllib.unquote(next_path))

        self.selenium.find_element_by_id('id_username').send_keys(self.get_username(user))
        self.selenium.find_element_by_id('id_password').send_keys(self.get_password(user))

        buttons = self.selenium.find_elements_by_tag_name('button')
        if not len(buttons):
            inputs = self.selenium.find_elements_by_tag_name('input')
            for i in inputs:
                if i.get_attribute('type') == 'submit':
                    buttons.append(i)
        buttons[0].click()


class NoHTML5SeleniumTestCase(SeleniumTestCase):
    """Run live server integration tests using the specified firefox binary,
       which does not support our required HTML5 functionality.

        HTML5 ref:
       https://html5test.com/compare/feature/security-sandbox.html
    """

    firefox_path = '/opt/ff/firefox-16.0/firefox'

    @classmethod
    def getWebDriver(cls, **kwargs):
        firefox_binary = FirefoxBinary(firefox_path=cls.firefox_path)
        return super(NoHTML5SeleniumTestCase, cls).getWebDriver(firefox_binary=firefox_binary)


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

    # Get current page id, if any
    old_page_id = None
    try:
        old_page = browser.find_element_by_tag_name('html')
        old_page_id = old_page.id
    except NoSuchElementException:
        old_page_id = None

    # Yield to run requested functions
    yield

    def page_has_loaded():
        try:
            new_page = browser.find_element_by_tag_name('html')
            return new_page.id != old_page_id
        except NoSuchElementException:
            return False

    wait_for(page_has_loaded)

def patch_broken_pipe_error():
    """Monkey Patch BaseServer.handle_error to not write
    a stacktrace to stderr on broken pipe.
    http://stackoverflow.com/a/22618740/362702"""
    import sys
    from SocketServer import BaseServer
    from wsgiref import handlers

    handle_error = BaseServer.handle_error
    log_exception = handlers.BaseHandler.log_exception

    def is_broken_pipe_error():
        type, err, tb = sys.exc_info()
        return (repr(err) == "error(32, 'Broken pipe')"
            or repr(err) == "error(104, 'Connection reset by peer')")

    def my_handle_error(self, request, client_address):
        if not is_broken_pipe_error():
            handle_error(self, request, client_address)

    def my_log_exception(self, exc_info):
        if not is_broken_pipe_error():
            log_exception(self, exc_info)

    BaseServer.handle_error = my_handle_error
    handlers.BaseHandler.log_exception = my_log_exception

patch_broken_pipe_error()
