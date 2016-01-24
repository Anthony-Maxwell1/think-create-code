import re
import time
import os
import urllib
from urlparse import urlparse
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.conf import settings

from django_adelaidex.util.test import SeleniumTestCase, wait_for_page_load
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
        self.selenium.find_element_by_id('login').click()

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
                         '%slti/user/' % admin_index_url)

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
                         '%slti/user/' % admin_index_url)


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

        # Search Artwork
        form = self.selenium.find_elements_by_css_selector('#artwork-search')
        self.assertEqual(len(form), 1)

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

        # Terms
        link = self.selenium.find_element_by_id('footer-terms')
        terms_url = '%s%s' % (self.live_server_url, reverse('terms'))
        self.assertEqual(link.get_attribute('href'), terms_url)
        self.assertEqual(link.text, 'Terms of Use')

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

        # Search Artwork
        form = self.selenium.find_elements_by_css_selector('#artwork-search')
        self.assertEqual(len(form), 1)

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

        # Terms
        link = self.selenium.find_element_by_id('footer-terms')
        terms_url = '%s%s' % (self.live_server_url, reverse('terms'))
        self.assertEqual(link.get_attribute('href'), terms_url)
        self.assertEqual(link.text, 'Terms of Use')

        # Profile
        link = self.selenium.find_element_by_id('nav-profile')
        profile_url = '%s%s?next=%s' % (self.live_server_url, reverse('lti-user-profile'), reverse('home'))
        self.assertEqual(link.get_attribute('href'), profile_url)
        self.assertEqual(link.text, '%s Profile' % self.user)

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

        # Search Artwork
        form = self.selenium.find_elements_by_css_selector('#artwork-search')
        self.assertEqual(len(form), 1)

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

        # Terms
        link = self.selenium.find_element_by_id('footer-terms')
        terms_url = '%s%s' % (self.live_server_url, reverse('terms'))
        self.assertEqual(link.get_attribute('href'), terms_url)
        self.assertEqual(link.text, 'Terms of Use')

        # Profile
        link = self.selenium.find_element_by_id('nav-profile')
        profile_url = '%s%s?next=%s' % (self.live_server_url, reverse('lti-user-profile'), reverse('home'))
        self.assertEqual(link.get_attribute('href'), profile_url)
        self.assertEqual(link.text, '%s Profile' % self.staff_user)

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


class GalleryArtworkSearchIntegrationTests(SeleniumTestCase):
    '''Test the artwork search form'''

    def test_artwork_list(self):
        # Visit Add Artwork page
        self.performLogin(user='student')
        home_url = '%s%s' % (self.live_server_url, reverse('home'))
        add_url = '%s%s' % (self.live_server_url, reverse('artwork-add'))
        self.selenium.get(add_url)

        # Hitting search with no term redirects to home page
        form = self.selenium.find_element_by_id('artwork-search')
        button = form.find_element_by_css_selector('button')
        site_url = '%s%s' % (self.live_server_url, reverse('home'))

        # Ensure we're redirected to home page
        with wait_for_page_load(self.selenium):
            button.click()
        self.assertEquals(home_url, self.selenium.current_url)

    def test_artwork_search(self):
        self.performLogin(user='student')

        form = self.selenium.find_element_by_id('artwork-search')
        q = form.find_element_by_css_selector('[name=q]')
        q.send_keys('game')
        button = form.find_element_by_css_selector('button')
        site_url = '%s%s' % (self.live_server_url, reverse('home'))

        # Ensure we're redirected to google.com with the correct params set in url
        with wait_for_page_load(self.selenium):
            button.click()
        self.assertIn('google.com', self.selenium.current_url)
        q_str = 'q=site:%s' % urllib.quote('%s game' % site_url, '')
        self.assertIn(q_str, self.selenium.current_url)


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


class TestHelpView(SeleniumTestCase):
    """Ensure Help page is visible to public"""

    def test_public_get(self):
        help_url = '%s%s' % (self.live_server_url, reverse('help'))
        self.selenium.get(help_url)
        self.assertEqual(self.selenium.current_url, help_url)

        self.assertEquals(len(self.selenium.find_elements_by_id('help-content')), 1)
        self.assertEquals(len(self.selenium.find_elements_by_tag_name('h1')), 1)


class TestTermsView(SeleniumTestCase):
    """Ensure Terms of Use page is visible to public"""

    def test_public_get(self):
        terms_url = '%s%s' % (self.live_server_url, reverse('terms'))
        self.selenium.get(terms_url)
        self.assertEqual(self.selenium.current_url, terms_url)

        self.assertEquals(len(self.selenium.find_elements_by_id('terms-content')), 1)
        self.assertEquals(len(self.selenium.find_elements_by_tag_name('h1')), 1)
