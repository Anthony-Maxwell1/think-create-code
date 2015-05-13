import re
import time
import os
import urllib
from urlparse import urlparse
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test.utils import override_settings
from django.contrib.auth import get_user_model
from selenium.common.exceptions import NoSuchElementException

from uofa.test import SeleniumTestCase, InactiveUserSetUp, TestOverrideSettings, wait_for_page_load
from selenium.common.exceptions import NoSuchElementException
from gallery.views import ShareView
from artwork.models import Artwork


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

        # 3. logout redirects to home
        logout_url = '%s%s' % (self.live_server_url, reverse('logout'))
        home_url = '%s%s' % (self.live_server_url, reverse('home'))
        self.selenium.get(logout_url)
        self.assertEqual(self.selenium.current_url, home_url)

        # 4. re-visit "add artwork", and ensure we got sent back to login
        self.selenium.get(add_url)
        self.assertEqual(self.selenium.current_url, '%s%s?next=%s' % (self.live_server_url, reverse('login'), reverse('artwork-add')))


class GalleryStaffAdminIntegrationTests(SeleniumTestCase):

    def setUp(self):
        super(GalleryStaffAdminIntegrationTests, self).setUp()

        # Load staff group fixtures data
        from django.core.management import call_command
        call_command("loaddata", 'fixtures/000_staff_group.json', verbosity=0)

        self.assertEquals(0, self.user.groups.count())
        self.assertEquals(1, self.staff_user.groups.count())
        self.assertEquals(1, self.super_user.groups.count())

    def test_public(self):

        self.performLogout()
        base_url = self.live_server_url
        self.selenium.get(base_url)
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('Administer')
        )

    def test_student(self):

        self.performLogout()
        self.performLogin('student')

        base_url = self.live_server_url
        self.selenium.get(base_url)
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('Administer')
        )

    def test_staff(self):

        self.performLogout()
        self.performLogin('staff')

        base_url = self.live_server_url
        self.selenium.get(base_url)

        admin_link = self.selenium.find_element_by_link_text('Administer')
        admin_link.click()

        admin_index_url = '%s%s' % (base_url, reverse('admin:index'))
        self.assertEqual(self.selenium.current_url, admin_index_url)

    def test_student_admin_login(self):

        base_url = self.live_server_url
        admin_login_path = reverse('admin:login')
        admin_login_url = '%s%s' % (base_url, admin_login_path)

        self.performLogout()
        self.selenium.get(admin_login_url)
        self._doLogin(user='student', login='admin:login')

        # Student user ends up back at the admin login page, with an error
        self.assertEqual(self.selenium.current_url, admin_login_url)
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.errornote').text,
            'Please enter the correct username and password for a staff account.'
            ' Note that both fields may be case-sensitive.'
        )

    def test_staff_admin_login(self):

        base_url = self.live_server_url
        admin_index_path = reverse('admin:index')
        admin_index_url = '%s%s' % (base_url, admin_index_path)
        admin_login_url = '%s%s?next=%s' % (base_url, reverse('admin:login'), admin_index_path)

        self.performLogout()
        self.selenium.get(admin_login_url)
        self.assertLogin(user='staff', login='admin:login', next_path=admin_index_path)

        self.assertEqual(self.selenium.find_element_by_css_selector('.model-artwork a').get_attribute('href'),
                         '%sartwork/artwork/' % admin_index_url)
        self.assertEqual(self.selenium.find_element_by_css_selector('.model-group a').get_attribute('href'),
                         '%sauth/group/' % admin_index_url)
        self.assertEqual(self.selenium.find_element_by_css_selector('.model-exhibition a').get_attribute('href'),
                         '%sexhibitions/exhibition/' % admin_index_url)
        self.assertEqual(self.selenium.find_element_by_css_selector('.model-submission a').get_attribute('href'),
                         '%ssubmissions/submission/' % admin_index_url)
        self.assertEqual(self.selenium.find_element_by_css_selector('.model-user a').get_attribute('href'),
                         '%suofa/user/' % admin_index_url)

    def test_super_admin_login(self):

        base_url = self.live_server_url
        admin_index_path = reverse('admin:index')
        admin_index_url = '%s%s' % (base_url, admin_index_path)
        admin_login_url = '%s%s?next=%s' % (base_url, reverse('admin:login'), admin_index_path)

        self.performLogout()
        self.selenium.get(admin_login_url)
        self.assertLogin(user='super', login='admin:login', next_path=admin_index_path)

        self.assertEqual(self.selenium.find_element_by_css_selector('.model-artwork a').get_attribute('href'),
                         '%sartwork/artwork/' % admin_index_url)
        self.assertEqual(self.selenium.find_element_by_css_selector('.model-group a').get_attribute('href'),
                         '%sauth/group/' % admin_index_url)
        self.assertEqual(self.selenium.find_element_by_css_selector('.model-exhibition a').get_attribute('href'),
                         '%sexhibitions/exhibition/' % admin_index_url)
        self.assertEqual(self.selenium.find_element_by_css_selector('.model-submission a').get_attribute('href'),
                         '%ssubmissions/submission/' % admin_index_url)
        self.assertEqual(self.selenium.find_element_by_css_selector('.model-user a').get_attribute('href'),
                         '%suofa/user/' % admin_index_url)


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

    def test_public_nav_links(self):
        base_url = self.live_server_url
        self.selenium.get(base_url)

        # My Studio
        link = self.selenium.find_element_by_id('nav-my-artwork')
        studio_url = '%s%s' % (self.live_server_url, reverse('artwork-studio'))
        self.assertEqual(link.get_attribute('href'), studio_url)
        self.assertEqual(link.text, 'My Studio')

        # Shared Artwork
        link = self.selenium.find_element_by_id('nav-shared-artwork')
        artwork_url = '%s%s' % (self.live_server_url, reverse('artwork-shared'))
        self.assertEqual(link.get_attribute('href'), artwork_url)
        self.assertEqual(link.text, 'Artwork')

        # Exhibitions
        link = self.selenium.find_element_by_id('nav-exhibitions')
        exhibitions_url = '%s%s' % (self.live_server_url, reverse('exhibition-list'))
        self.assertEqual(link.get_attribute('href'), exhibitions_url)
        self.assertEqual(link.text, 'Exhibitions')

        # Help
        link = self.selenium.find_element_by_id('nav-help')
        help_url = '%s%s' % (self.live_server_url, reverse('help'))
        self.assertEqual(link.get_attribute('href'), help_url)
        self.assertEqual(link.text, 'Help')

        # Sign in
        link = self.selenium.find_element_by_id('nav-signin')
        login_url = '%s%s?next=%s' % (self.live_server_url, reverse('login'), reverse('home'))
        self.assertEqual(link.get_attribute('href'), login_url)
        self.assertEqual(link.text, 'Sign in')

        # No Administer
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('nav-admin')
        )

        # No Profile
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('nav-profile')
        )

        # No sign out
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('nav-signout')
        )

    def test_student_nav_links(self):
        self.performLogin(user='student')

        # My Studio
        link = self.selenium.find_element_by_id('nav-my-artwork')
        studio_url = '%s%s' % (self.live_server_url, reverse('artwork-studio'))
        self.assertEqual(link.get_attribute('href'), studio_url)
        self.assertEqual(link.text, 'My Studio')

        # Shared Artwork
        link = self.selenium.find_element_by_id('nav-shared-artwork')
        artwork_url = '%s%s' % (self.live_server_url, reverse('artwork-shared'))
        self.assertEqual(link.get_attribute('href'), artwork_url)
        self.assertEqual(link.text, 'Artwork')

        # Exhibitions
        link = self.selenium.find_element_by_id('nav-exhibitions')
        exhibitions_url = '%s%s' % (self.live_server_url, reverse('exhibition-list'))
        self.assertEqual(link.get_attribute('href'), exhibitions_url)
        self.assertEqual(link.text, 'Exhibitions')

        # Help
        link = self.selenium.find_element_by_id('nav-help')
        help_url = '%s%s' % (self.live_server_url, reverse('help'))
        self.assertEqual(link.get_attribute('href'), help_url)
        self.assertEqual(link.text, 'Help')

        # Profile
        link = self.selenium.find_element_by_id('nav-profile')
        profile_url = '%s%s?next=%s' % (self.live_server_url, reverse('user-profile'), reverse('home'))
        self.assertEqual(link.get_attribute('href'), profile_url)
        self.assertEqual(link.text, '%s' % self.user)

        # No Administer
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('nav-admin')
        )

        # No sign in
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('nav-signin')
        )

        # No sign out
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('nav-signout')
        )

    def test_staff_nav_links(self):
        self.performLogin(user='staff')

        # My Studio
        link = self.selenium.find_element_by_id('nav-my-artwork')
        studio_url = '%s%s' % (self.live_server_url, reverse('artwork-studio'))
        self.assertEqual(link.get_attribute('href'), studio_url)
        self.assertEqual(link.text, 'My Studio')

        # Shared Artwork
        link = self.selenium.find_element_by_id('nav-shared-artwork')
        artwork_url = '%s%s' % (self.live_server_url, reverse('artwork-shared'))
        self.assertEqual(link.get_attribute('href'), artwork_url)
        self.assertEqual(link.text, 'Artwork')

        # Exhibitions
        link = self.selenium.find_element_by_id('nav-exhibitions')
        exhibitions_url = '%s%s' % (self.live_server_url, reverse('exhibition-list'))
        self.assertEqual(link.get_attribute('href'), exhibitions_url)
        self.assertEqual(link.text, 'Exhibitions')

        # Help
        link = self.selenium.find_element_by_id('nav-help')
        help_url = '%s%s' % (self.live_server_url, reverse('help'))
        self.assertEqual(link.get_attribute('href'), help_url)
        self.assertEqual(link.text, 'Help')

        # Profile
        link = self.selenium.find_element_by_id('nav-profile')
        profile_url = '%s%s?next=%s' % (self.live_server_url, reverse('user-profile'), reverse('home'))
        self.assertEqual(link.get_attribute('href'), profile_url)
        self.assertEqual(link.text, '%s' % self.staff_user)

        # Administer
        link = self.selenium.find_element_by_id('nav-admin')
        admin_url = '%s%s' % (self.live_server_url, reverse('admin:index'))
        self.assertEqual(link.get_attribute('href'), admin_url)
        self.assertEqual(link.text, 'Administer')

        # No sign in
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('nav-signin')
        )

        # No sign out
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('nav-signout')
        )


class ShareViewIntegrationTest(SeleniumTestCase):
    '''Test the Share view, used by the share links'''

    def test_share_view(self):
        share_path = reverse('share')
        share_url = '%s%s' % (self.live_server_url, share_path)
        home_path = reverse('home')
        home_url = '%s%s' % (self.live_server_url, home_path)

        # Ensure redirects to home
        self.selenium.get(share_url)
        time.sleep(1)
        self.assertEqual(self.selenium.current_url, home_url)

    def test_get_share_url(self):
        share_url = ShareView.get_share_url()
        home_path = reverse('home')
        home_url = '%s%s' % (self.live_server_url, home_path)

        # Ensure redirects to home
        self.selenium.get(share_url)
        time.sleep(1)
        self.assertEqual(self.selenium.current_url, home_url)

    def test_get_share_url_home(self):
        home_path = reverse('home')
        share_url = ShareView.get_share_url(home_path)
        home_url = '%s%s' % (self.live_server_url, home_path)

        # Ensure redirects to home
        self.selenium.get(share_url)
        time.sleep(1)
        self.assertEqual(self.selenium.current_url, home_url)

    def test_reverse_share_url(self):
        share_url = ShareView.reverse_share_url()
        home_path = reverse('home')
        home_url = '%s%s' % (self.live_server_url, home_path)

        # Ensure redirects to home
        self.selenium.get(share_url)
        time.sleep(1)
        self.assertEqual(self.selenium.current_url, home_url)

    def test_reverse_share_url_home(self):
        share_url = ShareView.reverse_share_url('home')
        home_path = reverse('home')
        home_url = '%s%s' % (self.live_server_url, home_path)

        # Ensure redirects to home
        self.selenium.get(share_url)
        time.sleep(1)
        self.assertEqual(self.selenium.current_url, home_url)

    def test_reverse_share_url_artwork_view(self):
        share_url = ShareView.reverse_share_url('artwork-view', kwargs={'pk': 1})
        artwork_path = reverse('artwork-view', kwargs={'pk': 1})
        artwork_url = '%s%s' % (self.live_server_url, artwork_path)

        # Ensure redirects to artwork view
        self.selenium.get(share_url)
        time.sleep(1)
        self.assertEqual(self.selenium.current_url, artwork_url)

    def test_reverse_share_url_exhibition_view(self):
        share_url = ShareView.reverse_share_url('exhibition-view', kwargs={'pk': 1})
        exhibition_path = reverse('exhibition-view', kwargs={'pk': 1})
        exhibition_url = '%s%s' % (self.live_server_url, exhibition_path)

        # Ensure redirects to exhibition view
        self.selenium.get(share_url)
        time.sleep(1)
        self.assertEqual(self.selenium.current_url, exhibition_url)

    '''Test the Share view, used by the share links.
       Have to use urllib to fetch the (bit.ly) external share urls,
       and run the Selenium browser to perform the redirects.'''

    def assertShareUrlRedirects(self, redirect_url):
        parsed_redirect = urlparse(redirect_url)
        response = urllib.urlopen(redirect_url)
        target_url = response.geturl()
        parsed_target = urlparse(target_url)

        self.assertEqual(response.getcode(), 200)
        self.assertEqual(parsed_redirect.netloc, urlparse(settings.SHARE_URL).netloc)
        self.assertEqual(parsed_target.netloc, os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'])
        self.assertEqual(parsed_target.path, reverse('share'))

        self.assertEqual(parsed_redirect.scheme, 'https')
        self.assertEqual(parsed_redirect.query,  parsed_target.query)
        # I wish this worked.. since it's the meat of the share request.
        # But since servers don't care about fragments, we can't see it in the target :(
        # Have to rely on the integration tests instead.
        #self.assertEqual(parsed_redirect.fragment, parsed_target.fragment)

    def test_share_url_redirect(self):
        share_url = ShareView.get_share_url()
        self.assertShareUrlRedirects(share_url)

    def test_share_url_home_redirects(self):
        share_url = ShareView.get_share_url(reverse('home'))
        self.assertShareUrlRedirects(share_url)

    def test_reverse_share_url_redirects(self):
        share_url = ShareView.reverse_share_url()
        self.assertShareUrlRedirects(share_url)

    def test_reverse_share_url_home_redirects(self):
        share_url = ShareView.reverse_share_url('home')
        self.assertShareUrlRedirects(share_url)

    def test_reverse_share_url_artwork_view_redirects(self):
        share_url = ShareView.reverse_share_url('artwork-view', kwargs={'pk': 1})
        self.assertShareUrlRedirects(share_url)

    def test_reverse_share_url_exhibition_view_redirects(self):
        share_url = ShareView.reverse_share_url('exhibition-view', kwargs={'pk': 1})
        self.assertShareUrlRedirects(share_url)


class LTILoginViewTest(TestOverrideSettings, SeleniumTestCase):

    # Set the LTI Login Url, and use lti-403 as the login URL
    @override_settings(LTI_LOGIN_URL='https://www.google.com.au')
    def test_view(self):

        self.reload_urlconf()

        # ensure no cookies set
        cookies = self.selenium.get_cookies()
        self.assertEqual(len(cookies), 0)

        # get login view, with next param set
        target = reverse('artwork-studio')
        target_url = '%s%s' % (self.live_server_url, target)
        querystr = '?next=' + target
        lti_login = reverse('lti-login') + querystr
        lti_login_url = '%s%s%s' % (self.live_server_url, lti_login, querystr)

        self.selenium.get(lti_login_url)

        # ensure it redirects to the LTI_LOGIN_URL
        login_regex = re.compile('^%s' % settings.LTI_LOGIN_URL)
        self.assertRegexpMatches(self.selenium.current_url, login_regex)

        # ensure cookie was set
        self.selenium.get(target_url)
        cookies = self.selenium.get_cookies()
        self.assertEqual(len(cookies), 1)
        self.assertEqual(cookies[0]['name'], settings.LTI_PERSIST_NAME)


class LTIEnrolViewTest(SeleniumTestCase):

    def test_view(self):

        # ensure no cookies set
        cookies = self.selenium.get_cookies()
        self.assertEqual(len(cookies), 0)

        # get enrol view, with next param set
        target = reverse('artwork-studio')
        target_url = '%s%s' % (self.live_server_url, target)
        querystr = '?next=' + target
        lti_enrol = reverse('lti-enrol') + querystr
        lti_enrol_url = '%s%s%s' % (self.live_server_url, lti_enrol, querystr)

        self.selenium.get(lti_enrol_url)

        # ensure it redirects to the LTI_ENROL_URL
        enrol_regex = re.compile(r'^%s' % settings.LTI_ENROL_URL)
        self.assertRegexpMatches(self.selenium.current_url, enrol_regex)

        # ensure cookie was set
        self.selenium.get(target_url)
        cookies = self.selenium.get_cookies()
        self.assertEqual(len(cookies), 2)
        self.assertEqual(cookies[0]['name'], settings.LTI_PERSIST_NAME)


class LTIEntryViewTest(SeleniumTestCase):

    def test_default_view(self):

        # ensure we're logged out
        self.performLogout()

        lti_entry_path = reverse('lti-entry')
        lti_entry = '%s%s' % (self.live_server_url, lti_entry_path)
        home_url = '%s%s' % (self.live_server_url, reverse('home'))

        # lti-entry redirects to login
        self.selenium.get(lti_entry)
        self.assertLogin(lti_entry_path)

        # then shows form
        first_name = self.selenium.find_element_by_id('id_first_name')
        self.assertIsNotNone(first_name)

        first_name.send_keys('Username')

        save = self.selenium.find_element_by_id('save_user')
        with wait_for_page_load(self.selenium):
            save.click()

        # Ensure we're redirected to home
        self.assertEqual(self.selenium.current_url, home_url)

    def test_custom_next_view(self):

        # ensure we're logged out
        self.performLogout()

        lti_path = reverse('lti-entry')
        lti_entry = '%s%s' % (self.live_server_url, lti_path)
        artwork_path = reverse('artwork-add')
        artwork_url = '%s%s' % (self.live_server_url, artwork_path)

        # lti-entry redirects to login
        self.selenium.get(lti_entry)
        self.assertLogin(lti_path)

        # then shows form
        first_name = self.selenium.find_element_by_id('id_first_name')
        self.assertIsNotNone(first_name)

        first_name.send_keys('Username')

        custom_next = self.selenium.find_element_by_id('id_custom_next')
        self.selenium.execute_script('''
            var elem = arguments[0];
            var value = arguments[1];
            elem.value = value;
        ''', custom_next, artwork_path)

        save = self.selenium.find_element_by_id('save_user')
        with wait_for_page_load(self.selenium):
            save.click()

        # Ensure we're redirected to the artwork url
        self.assertEqual(self.selenium.current_url, artwork_url)


class LTIInactiveEntryViewTest(InactiveUserSetUp, SeleniumTestCase):

    def test_default_view(self):

        lti_entry_path = reverse('lti-entry')
        lti_entry = '%s%s' % (self.live_server_url, lti_entry_path)
        inactive_url = '%s%s' % (self.live_server_url, reverse('lti-inactive'))

        # login inactive user
        self.performLogin(user="inactive")

        # lti-entry redirects inactive users to lti-inactive
        self.selenium.get(lti_entry)

        # should have redirected to lti-inactive
        self.assertEqual(self.selenium.current_url, inactive_url)


class LTIPermissionDeniedViewTest(TestOverrideSettings, SeleniumTestCase):

    # Set the LTI Login Url, and use lti-403 as the login URL
    @override_settings(LTI_LOGIN_URL='https://www.google.com.au')
    def test_view(self):

        self.reload_urlconf()

        # ensure we're logged out
        self.performLogout()

        target_path = reverse('artwork-studio')
        target_url = '%s%s' % (self.live_server_url, target_path)

        querystr = '?next=' + target_path
        lti_403 = '%s%s%s' % (self.live_server_url, reverse('login'), querystr)
        lti_login = '%s%s%s' % (self.live_server_url, reverse('lti-login'), querystr)
        lti_enrol = '%s%s%s' % (self.live_server_url, reverse('lti-enrol'), querystr)

        # ensure login-required URL redirects to configured login page (lti-403)
        self.selenium.get(target_url)
        self.assertEqual(self.selenium.current_url, lti_403)

        # visit lti-403
        course_link = self.selenium.find_element_by_link_text(settings.LTI_LINK_TEXT)
        self.assertEqual(course_link.get_attribute('href'), lti_login)

        login_link = self.selenium.find_element_by_link_text('Go to %s' % settings.LTI_LINK_TEXT)
        self.assertEqual(login_link.get_attribute('href'), lti_login)

        enrol_link = self.selenium.find_element_by_link_text('Enrol in %s' % settings.LTI_LINK_TEXT)
        self.assertEqual(enrol_link.get_attribute('href'), lti_enrol)


class LTILoginEntryViewTest(TestOverrideSettings, SeleniumTestCase):
    '''Test the full LTI Login/Entry redirect cycle'''

    # Set the LTI Login Url, and use lti-403 as the login URL
    @override_settings(LTI_LOGIN_URL='https://www.google.com.au')
    def _performRedirectTest(self, target, target_redirect=None):

        # url config is dependent on app settings, so reload
        self.reload_urlconf()

        # ensure we're logged out
        self.performLogout()

        # ensure we've got no LTI cookie set
        self.selenium.delete_all_cookies()
        cookies = self.selenium.get_cookies()
        self.assertEqual(len(cookies), 0)

        # visit the lti login redirect url, with the target in the querystring
        querystr = '?next=' + target
        target_url = '%s%s' % (self.live_server_url, target)
        target_redirect_url = None
        if target_redirect:
            target_redirect_url = '%s%s' % (self.live_server_url, target_redirect)

        lti_login = reverse('lti-login') + querystr
        lti_login_url = '%s%s' % (self.live_server_url, lti_login)
        self.selenium.get(lti_login_url)
        self.assertRegexpMatches(self.selenium.current_url, settings.LTI_LOGIN_URL)

        # ensure cookie was set
        self.selenium.get(target_url)
        cookies = self.selenium.get_cookies()
        self.assertEqual(len(cookies), 1)
        self.assertEqual(cookies[0]['name'], settings.LTI_PERSIST_NAME)

        # lti-entry redirects to login
        lti_entry = reverse('lti-entry')
        lti_entry_url = '%s%s' % (self.live_server_url, lti_entry)

        # need to force auth real login here to get past lti-entry auth
        self.performLogin(login='auth-login')
        self.selenium.get(lti_entry_url)

        # fill in form
        first_name = self.selenium.find_element_by_id('id_first_name')
        self.assertIsNotNone(first_name)
        first_name.send_keys('Username')

        save = self.selenium.find_element_by_id('save_user')
        with wait_for_page_load(self.selenium):
            save.click()

        # and ensure we're redirected back to target
        if target_redirect:
            self.assertEqual(self.selenium.current_url, target_redirect_url)
        else:
            self.assertEqual(self.selenium.current_url, target_url)

        # ensure cookie was cleared
        cookies = self.selenium.get_cookies()
        self.assertEqual(len(cookies), 2, cookies)
        self.assertEqual(cookies[0]['name'], 'sessionid')
        self.assertEqual(cookies[1]['name'], 'csrftoken')

        # double-check the cookie has cleared by revisiting lti-entry, and
        # ensuring we're redirected properly
        for custom_next in (reverse('artwork-add'), None):
            self.selenium.get(lti_entry_url)

            # fill in form
            first_name = self.selenium.find_element_by_id('id_first_name')
            self.assertIsNotNone(first_name)
            first_name.send_keys('Username')

            if custom_next:
                custom_next_url = '%s%s' % (self.live_server_url, custom_next)
                custom_next_field = self.selenium.find_element_by_id('id_custom_next')
                self.selenium.execute_script('''
                    var elem = arguments[0];
                    var value = arguments[1];
                    elem.value = value;
                ''', custom_next_field, custom_next)
            else:
                custom_next_url = '%s%s' % (self.live_server_url, reverse('home'))

            save = self.selenium.find_element_by_id('save_user')
            with wait_for_page_load(self.selenium):
                save.click()

            # Ensure we're redirected to the artwork url
            self.assertEqual(self.selenium.current_url, custom_next_url)

        return True

    def test_my_studio(self):
        path = reverse('artwork-studio') # redirects to artwork-author-list
        redirect_path = reverse('artwork-author-list', kwargs={'author': self.user.id, 'shared': 0})
        ok = self._performRedirectTest(path, redirect_path)
        self.assertTrue(ok)

    def test_artwork_add(self):
        path = reverse('artwork-add')
        ok = self._performRedirectTest(path)
        self.assertTrue(ok)

    def test_private_artwork(self):
        private_artwork = Artwork.objects.create(title='Private Artwork', code='// code goes here', author=self.user)
        path = reverse('artwork-view', kwargs={'pk': private_artwork.id})
        ok = self._performRedirectTest(path)
        self.assertTrue(ok)


class UserProfileViewTest(SeleniumTestCase):

    def test_anon_view(self):
        '''Profile View requires login'''
        profile_path = reverse('user-profile')
        profile_url = '%s%s' % (self.live_server_url, profile_path)

        login_path = reverse('login')
        login_url = '%s%s?next=%s' % (self.live_server_url, login_path, profile_path)

        self.selenium.get(profile_url)
        self.assertEqual(self.selenium.current_url, login_url)

    def test_student_view(self):
        '''Students can login'''
        profile_path = reverse('user-profile')
        profile_url = '%s%s' % (self.live_server_url, profile_path)

        self.selenium.get(profile_url)
        self.assertLogin(profile_path, user="student")
        self.assertEqual(self.selenium.current_url, profile_url)

        labels = self.selenium.find_elements_by_tag_name('label')
        self.assertEqual(len(labels), 4)
        self.assertEqual(labels[0].text, 'Nickname:')
        self.assertEqual(labels[1].text, '')
        self.assertEqual(labels[1].get_attribute('class'), 'error')
        self.assertEqual(labels[2].text, 'Timezone:')
        self.assertEqual(labels[3].text, '')
        self.assertEqual(labels[3].get_attribute('class'), 'error')

    def test_staff_view(self):
        '''Staff can login'''
        profile_path = reverse('user-profile')
        profile_url = '%s%s' % (self.live_server_url, profile_path)

        self.selenium.get(profile_url)
        self.assertLogin(profile_path, user="staff")
        self.assertEqual(self.selenium.current_url, profile_url)

        labels = self.selenium.find_elements_by_tag_name('label')
        self.assertEqual(len(labels), 5)
        self.assertEqual(labels[0].text, 'Staff access:')
        self.assertEqual(labels[1].text, 'Nickname:')
        self.assertEqual(labels[2].text, '')
        self.assertEqual(labels[2].get_attribute('class'), 'error')
        self.assertEqual(labels[3].text, 'Timezone:')
        self.assertEqual(labels[4].text, '')
        self.assertEqual(labels[4].get_attribute('class'), 'error')

    def test_super_view(self):
        '''Superuser can login'''
        profile_path = reverse('user-profile')
        profile_url = '%s%s' % (self.live_server_url, profile_path)

        self.selenium.get(profile_url)
        self.assertLogin(profile_path, user="super")
        self.assertEqual(self.selenium.current_url, profile_url)

        labels = self.selenium.find_elements_by_tag_name('label')
        self.assertEqual(len(labels), 5)
        self.assertEqual(labels[0].text, 'Staff access:')
        self.assertEqual(labels[1].text, 'Nickname:')
        self.assertEqual(labels[2].text, '')
        self.assertEqual(labels[2].get_attribute('class'), 'error')
        self.assertEqual(labels[3].text, 'Timezone:')
        self.assertEqual(labels[4].text, '')
        self.assertEqual(labels[4].get_attribute('class'), 'error')

    def test_post_username_required(self):
        profile_path = reverse('user-profile')
        profile_url = '%s%s' % (self.live_server_url, profile_path)

        home_path = reverse('home')
        home_url = '%s%s' % (self.live_server_url, home_path)

        self.selenium.get(profile_url)
        self.assertLogin(profile_path, user="student")
        self.assertEqual(self.selenium.current_url, profile_url)

        labels = self.selenium.find_elements_by_tag_name('label')
        self.assertEqual(len(labels), 4)
        self.assertEqual(labels[0].text, 'Nickname:')
        self.assertEqual(labels[1].text, '')
        self.assertEqual(labels[1].get_attribute('class'), 'error')
        self.assertEqual(labels[2].text, 'Timezone:')
        self.assertEqual(labels[3].text, '')
        self.assertEqual(labels[3].get_attribute('class'), 'error')

        form_data = {}
        for field, value in form_data.iteritems():
            self.selenium.find_element_by_id('id_' + field).send_keys(value)
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_user').click()

        labels = self.selenium.find_elements_by_tag_name('label')
        self.assertEqual(len(labels), 4)
        self.assertEqual(labels[0].text, 'Nickname:')
        self.assertEqual(labels[1].text, 'This field is required.')
        self.assertEqual(labels[1].get_attribute('class'), 'error')
        self.assertEqual(labels[2].text, 'Timezone:')
        self.assertEqual(labels[3].text, '')
        self.assertEqual(labels[3].get_attribute('class'), 'error')

        form_data = {'first_name': 'MyNickname'}
        for field, value in form_data.iteritems():
            self.selenium.find_element_by_id('id_' + field).send_keys(value)
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_user').click()

        # should be redirected to home
        self.assertEqual(self.selenium.current_url, home_url)

        # POST should have set user nickname, used default timezone
        user = get_user_model().objects.get(username=self.get_username('student'))
        self.assertEqual(user.first_name, form_data['first_name'])
        self.assertEqual(user.time_zone, 'UTC')

    def test_post_timezone(self):
        profile_path = reverse('user-profile')
        profile_url = '%s%s' % (self.live_server_url, profile_path)

        home_path = reverse('home')
        home_url = '%s%s' % (self.live_server_url, home_path)

        self.selenium.get(profile_url)
        self.assertLogin(profile_path, user="student")

        form_data = {'first_name': 'MyNickname', 'time_zone': 'Australia/Adelaide'}
        for field, value in form_data.iteritems():
            self.selenium.find_element_by_id('id_' + field).send_keys(value)
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_user').click()

        # should be redirected to home
        self.assertEqual(self.selenium.current_url, home_url)

        # POST should have set user nickname, timezone
        user = get_user_model().objects.get(username=self.get_username('student'))
        self.assertEqual(user.first_name, form_data['first_name'])
        self.assertEqual(user.time_zone, form_data['time_zone'])

    def test_post_with_next(self):
        next_path = reverse('help')
        next_url = '%s%s' % (self.live_server_url, next_path)

        profile_path = '%s?next=%s' % (reverse('user-profile'), next_path)
        profile_url = '%s%s' % (self.live_server_url, profile_path)

        self.selenium.get(profile_url)
        self.assertLogin(profile_path, user="student")

        form_data = {'first_name': 'MyNickname'}
        for field, value in form_data.iteritems():
            self.selenium.find_element_by_id('id_' + field).send_keys(value)
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_user').click()

        # should be redirected to next_path
        self.assertEqual(self.selenium.current_url, next_url)

        # POST should have set user nickname, used default timezone
        user = get_user_model().objects.get(username=self.get_username('student'))
        self.assertEqual(user.first_name, form_data['first_name'])
        self.assertEqual(user.time_zone, 'UTC')

    def test_cancel_post_custom_next(self):
        next_path = reverse('help')
        next_url = '%s%s' % (self.live_server_url, next_path)

        profile_path = '%s?next=%s' % (reverse('user-profile'), next_path)
        profile_url = '%s%s' % (self.live_server_url, profile_path)

        self.selenium.get(profile_url)
        self.assertLogin(profile_path, user="student")

        form_data = {'first_name': 'MyNickname', 'time_zone': 'Australia/Adelaide'}
        for field, value in form_data.iteritems():
            self.selenium.find_element_by_id('id_' + field).send_keys(value)

        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('cancel_user').click()

        # should be redirected to next_path
        self.assertEqual(self.selenium.current_url, next_url)

        # POST should not have set user nickname, used default timezone
        user = get_user_model().objects.get(username=self.get_username('student'))
        self.assertEqual(user.first_name, '')
        self.assertEqual(user.time_zone, None)
