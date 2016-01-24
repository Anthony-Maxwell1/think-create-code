from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django_adelaidex.util.test import TestOverrideSettings


class GalleryAuthTests(TestOverrideSettings, TestCase):
    '''Test login urls'''

    @override_settings(ADELAIDEX_LTI={
        'ENROL_URL':None,
    })
    def test_auth_login(self):
        self.reload_urlconf()

        lti_login_path = reverse('lti-login')
        auth_login_path = reverse('auth-login')
        login_path = reverse('login')
        self.assertNotEquals(lti_login_path, auth_login_path)

        client = Client()
        response = client.get(login_path)
        self.assertFalse('view' in response.context)

    @override_settings(ADELAIDEX_LTI={
        'ENROL_URL':'https://www.google.com.au', 
    })
    def test_lti_login(self):
        self.reload_urlconf()

        lti_login_path = reverse('lti-login')
        auth_login_path = reverse('auth-login')
        login_path = reverse('login')
        self.assertNotEquals(lti_login_path, auth_login_path)

        client = Client()
        response = client.get(login_path)
        self.assertTrue('view' in response.context)
        view = response.context['view']
        self.assertEquals(str(type(view)), "<class 'django_adelaidex.lti.views.LTIPermissionDeniedView'>")


class ShareViewTest(TestCase):

    def test_share_view(self):
        client = Client()
        share_path = reverse('share')
        response = client.get(share_path)
        self.assertEqual(response.status_code, 200)
