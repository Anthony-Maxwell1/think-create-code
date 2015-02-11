from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
import urllib
from urlparse import urlparse
import os

from uofa.test import UserSetUp, SeleniumTestCase
from gallery.views import ShareView

class LTILoginViewTest(UserSetUp, TestCase):
    """LTI Login view tests."""

    def test_public_get(self):

        '''Unauthenticated GET users get redirected to basic login page'''
        client = Client()
        lti_login_path = reverse('lti-login')
        response = client.get(lti_login_path)

        login_path = '%s?next=%s' % (reverse('login'), lti_login_path)
        self.assertRedirects(response, login_path, status_code=302, target_status_code=200)

    def test_auth_get(self):

        '''Authenticated GET users are shown the lti-login page'''
        client = Client()
        lti_login_path = reverse('lti-login')
        response = self.assertLogin(client, lti_login_path)

        self.assertEqual(self.user, response.context['user'])
        self.assertEqual(1, len(response.context['form'].fields))
        self.assertIn('first_name', response.context['form'].fields)
        self.assertEqual(self.user, response.context['form'].instance)

    def test_auth_post(self):

        '''Authenticated POST users, without a nickname set, are shown the lti-login page'''
        client = Client()
        self.assertLogin(client, reverse('home'))

        lti_login_path = reverse('lti-login')
        response = client.post(lti_login_path)

        self.assertEqual(self.user, response.context['user'])
        self.assertEqual(1, len(response.context['form'].fields))
        self.assertIn('first_name', response.context['form'].fields)
        self.assertEqual(self.user, response.context['form'].instance)

    def test_nickname_post(self):

        '''Authenticated POST users, with a nickname set, are redirected to home'''
        self.user.first_name = "MyNickname"
        self.user.save()

        client = Client()
        home_path = reverse('home')
        self.assertLogin(client, home_path)

        lti_login_path = reverse('lti-login')
        response = client.post(lti_login_path)
        self.assertRedirects(response, home_path, status_code=302, target_status_code=200)

    def test_nickname_post_custom_next(self):

        '''Authenticated POST users, with a nickname set, are redirected to the
           path resolved by the custom_next post parameter.'''
        self.user.first_name = "MyNickname"
        self.user.save()

        client = Client()
        home_path = reverse('home')
        self.assertLogin(client, reverse('home'))

        lti_login_path = reverse('lti-login')
        list_path = reverse('exhibition-list')
        response = client.post(lti_login_path, {'custom_next': list_path})
        self.assertRedirects(response, list_path, status_code=302, target_status_code=200)

    def test_set_nickname(self):

        '''Update the authenticated user's nickname from the LTI login page'''
        self.user.first_name = "MyNickname"
        self.user.save()

        client = Client()
        home_path = reverse('home')
        self.assertLogin(client, home_path)

        lti_login_path = reverse('lti-login')
        form_data = {'first_name': 'AnotherNickname'}
        response = client.post(lti_login_path, form_data)

        self.assertRedirects(response, home_path, status_code=302, target_status_code=200)

        # Ensure the nickname was updated
        user = get_user_model().objects.get(username=self.user.username)
        self.assertEqual(user.first_name, form_data['first_name'])

    def test_set_empty_nickname(self):

        '''Non-empty nickname is required.'''
        client = Client()
        home_path = reverse('home')
        self.assertLogin(client, home_path)

        lti_login_path = reverse('lti-login')

        form_data = {'first_name': ''}
        response = client.post(lti_login_path, form_data)

        self.assertEqual(1, len(response.context['form'].fields))
        for field in response.context['form']:
            self.assertEquals(u'This field is required.', field.errors[0])

        form_data = {'first_name': '   '}
        response = client.post(lti_login_path, form_data)

        self.assertEqual(1, len(response.context['form'].fields))
        for field in response.context['form']:
            self.assertEquals(u'Please enter a valid nickname.', field.errors[0])

    def test_set_is_staff(self):

        '''Update the authenticated user's is_staff setting via the LTI POST parameters'''
        self.assertFalse(self.user.is_staff)

        client = Client()
        self.assertLogin(client, reverse('home'))

        # Fake the LTI session roles
        session = client.session
        session['LTI_LAUNCH'] = {
            'roles': ['Instructor',]
        }
        session.save()

        post_data = {
            'first_name': 'NickName',
        }
        lti_login_path = reverse('lti-login')
        response = client.post(lti_login_path, post_data)

        # Ensure the updated user is a staff member
        user = get_user_model().objects.get(username=self.user.username)
        self.assertTrue(user.is_staff)

    def test_set_is_student(self):

        '''Ensure the authenticated user remains non-staff even with LTI_LAUNCH roles'''
        self.assertFalse(self.user.is_staff)

        client = Client()
        self.assertLogin(client, reverse('home'))

        # Fake the LTI session roles
        session = client.session
        session['LTI_LAUNCH'] = {
            'roles': ['Student',]
        }
        session.save()

        post_data = {
            'first_name': 'NickName',
        }
        lti_login_path = reverse('lti-login')
        response = client.post(lti_login_path, post_data)

        # Ensure the updated user is still a student
        user = get_user_model().objects.get(username=self.user.username)
        self.assertFalse(user.is_staff)


class ShareViewTest(SeleniumTestCase):
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

        self.assertEqual(parsed_redirect.scheme, parsed_target.scheme)
        self.assertEqual(parsed_redirect.query,  parsed_target.query)
        # I wish this worked.. since it's the meat of the share request.
        # But since servers don't care about fragments, we can't see it in the target :(
        # Have to rely on the integration tests instead.
        #self.assertEqual(parsed_redirect.fragment, parsed_target.fragment)

    def test_share_view(self):
        client = Client()
        share_path = reverse('share')
        response = client.get(share_path)
        self.assertEqual(response.status_code, 200)

    def test_get_share_url(self):
        share_url = ShareView.get_share_url()
        self.assertShareUrlRedirects(share_url)

    def test_get_share_url_home(self):
        share_url = ShareView.get_share_url(reverse('home'))
        self.assertShareUrlRedirects(share_url)

    def test_reverse_share_url(self):
        share_url = ShareView.reverse_share_url()
        self.assertShareUrlRedirects(share_url)

    def test_reverse_share_url_home(self):
        share_url = ShareView.reverse_share_url('home')
        self.assertShareUrlRedirects(share_url)

    def test_reverse_share_url_artwork_view(self):
        share_url = ShareView.reverse_share_url('artwork-view', kwargs={'pk': 1})
        self.assertShareUrlRedirects(share_url)

    def test_reverse_share_url_exhibition_view(self):
        share_url = ShareView.reverse_share_url('exhibition-view', kwargs={'pk': 1})
        self.assertShareUrlRedirects(share_url)
