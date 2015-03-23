from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
import sys
from urlparse import urlparse

from uofa.test import UserSetUp, SeleniumTestCase, TestOverrideSettings
from artwork.models import Artwork


class LTIEntryViewTest(UserSetUp, TestCase):
    """LTI Login view tests."""

    def test_public_get(self):

        '''Unauthenticated GET users get redirected to basic login page'''
        client = Client()
        lti_login_path = reverse('lti-entry')
        response = client.get(lti_login_path)

        login_path = '%s?next=%s' % (reverse('login'), lti_login_path)
        self.assertRedirects(response, login_path, status_code=302, target_status_code=200)

    def test_auth_get(self):

        '''Authenticated GET users are shown the lti-entry page'''
        client = Client()
        lti_login_path = reverse('lti-entry')
        response = self.assertLogin(client, lti_login_path)

        self.assertEqual(self.user, response.context['user'])
        self.assertEqual(1, len(response.context['form'].fields))
        self.assertIn('first_name', response.context['form'].fields)
        self.assertEqual(self.user, response.context['form'].instance)

    def test_auth_post(self):

        '''Authenticated POST users, without a nickname set, are shown the lti-entry page'''
        client = Client()
        self.assertLogin(client, reverse('home'))

        lti_login_path = reverse('lti-entry')
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

        lti_login_path = reverse('lti-entry')
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

        lti_login_path = reverse('lti-entry')
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

        lti_login_path = reverse('lti-entry')
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

        lti_login_path = reverse('lti-entry')

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
        lti_login_path = reverse('lti-entry')
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
        lti_login_path = reverse('lti-entry')
        response = client.post(lti_login_path, post_data)

        # Ensure the updated user is still a student
        user = get_user_model().objects.get(username=self.user.username)
        self.assertFalse(user.is_staff)


class LTILoginViewTest(TestOverrideSettings, TestCase):

    # Set the LTI Login Url, and use lti-403 as the login URL
    @override_settings(LTI_LOGIN_URL='https://google.com')
    @override_settings(LOGIN_URL='lti-403')
    def test_view(self):

        self.reload_urlconf()

        client = Client()

        # ensure no cookies set
        cookie = client.cookies.get(settings.LTI_PERSIST_NAME)
        self.assertIsNone(cookie)

        # get login view, with next param set
        target = reverse('artwork-studio')
        querystr = '?next=' + target
        lti_login = reverse('lti-login') + querystr
        response = client.get(lti_login)

        # ensure it redirects to the LTI_LOGIN_URL
        self.assertRedirects(response, settings.LTI_LOGIN_URL, status_code=302, target_status_code=200)

        # ensure cookie was set
        response = client.get(target)
        cookie = client.cookies.get(settings.LTI_PERSIST_NAME)
        self.assertIsNotNone(cookie)


class LTIEnrolViewTest(TestCase):

    def test_view(self):

        client = Client()

        # ensure no cookies set
        cookie = client.cookies.get(settings.LTI_PERSIST_NAME)
        self.assertIsNone(cookie)

        # get enrol view, with next param set
        target = reverse('artwork-studio')
        querystr = '?next=' + target
        lti_enrol = reverse('lti-enrol') + querystr
        response = client.get(lti_enrol)

        # ensure it redirects to the LTI_ENROL_URL
        self.assertRedirects(response, settings.LTI_ENROL_URL, status_code=302, target_status_code=404)

        # ensure cookie was set
        response = client.get(target)
        cookie = client.cookies.get(settings.LTI_PERSIST_NAME)
        self.assertIsNotNone(cookie)


class LTIPermissionDeniedViewTest(TestOverrideSettings, TestCase):

    # Set the LTI Login Url, and use lti-403 as the login URL
    @override_settings(LTI_LOGIN_URL='https://google.com')
    @override_settings(LOGIN_URL='lti-403')
    def test_view(self):

        self.reload_urlconf()

        # ensure we're logged out
        client = Client()
        client.logout()

        # ensure login-required URL redirects to lti-403
        target = reverse('artwork-studio')
        querystr = '?next=' + target
        lti_403 = reverse('lti-403') + querystr
        response = client.get(target)
        self.assertRedirects(response, lti_403, status_code=302, target_status_code=200)

        # visit lti-403
        response = client.get(lti_403)
        self.assertEquals(response.context['lti_link_text'], settings.LTI_LINK_TEXT)
        self.assertEquals(response.context['lti_query_string'], querystr)


class LTILoginEntryViewTest(TestOverrideSettings, UserSetUp, TestCase):
    '''Test the full LTI Login/Entry redirect cycle'''

    # Set the LTI Login Url, and use lti-403 as the login URL
    @override_settings(LTI_LOGIN_URL='https://google.com')
    @override_settings(LOGIN_URL='lti-403')
    def _performRedirectTest(self, target, target_status_code=200):

        # url config is dependent on app settings, so reload
        self.reload_urlconf()

        client = Client()

        # ensure we're logged out
        client.logout()

        # ensure we've got no LTI cookie set
        cookie = client.cookies.get(settings.LTI_PERSIST_NAME)
        self.assertIsNone(cookie)

        # visit the lti login redirect url, with the target in the querystring
        querystr = '?next=' + target
        lti_login = reverse('lti-login') + querystr
        response = client.get(lti_login)
        self.assertRedirects(response, settings.LTI_LOGIN_URL, status_code=302, target_status_code=200)

        # ensure cookies were set
        cookie = client.cookies.get(settings.LTI_PERSIST_NAME)
        self.assertIsNotNone(cookie)

        # login, to bypass the LTI auth
        client.login(username=self.get_username(), password=self.get_password())

        # post to lti-entry, and ensure we're redirected back to target
        lti_entry = reverse('lti-entry')
        lti_post_param = {'first_name': 'Username'}
        response = client.post(lti_entry, lti_post_param)
        self.assertRedirects(response, target, status_code=302, target_status_code=target_status_code)
        
        # ensure the cookie has cleared by revisiting lti-entry, and ensuring
        # we're redirected properly
        for custom_next in (reverse('artwork-add'), None):
            if custom_next:
                lti_post_param['custom_next'] = custom_next
            else:
                del lti_post_param['custom_next']

            response = client.post(lti_entry, lti_post_param)
            self.assertRedirects(response, custom_next or reverse('home'), status_code=302, target_status_code=200)

        return True

    def test_my_studio(self):
        path = reverse('artwork-studio') # redirects to artwork-author-list
        ok = self._performRedirectTest(path, 302)
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


class ShareViewTest(TestCase):

    def test_share_view(self):
        client = Client()
        share_path = reverse('share')
        response = client.get(share_path)
        self.assertEqual(response.status_code, 200)
