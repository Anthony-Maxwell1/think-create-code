from django.test import TestCase
from django.utils import timezone
from django.contrib import auth
from django.test.client import Client
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.http import Http404, HttpResponse
from exceptions import Exception
from StringIO import StringIO
from mock import Mock
import pytz

from uofa.test import UserSetUp
from uofa.middleware import TimezoneMiddleware, WsgiLogErrors, P3PMiddleware

class TimezoneMiddlewareTest(TestCase):

    def setUp(self):
        super(TimezoneMiddlewareTest, self).setUp()
        self.tzm = TimezoneMiddleware()
        self.request = Mock()
        self.request.user = None
        self.UTC = timezone.get_default_timezone()

        # reset to default timezone
        timezone.deactivate()

    def test_no_user_process_request(self):
        self.assertEqual(self.request.user, None)
        self.assertEqual(timezone.get_current_timezone(), self.UTC)
        self.assertEqual(self.tzm.process_request(self.request), None)
        self.assertEqual(timezone.get_current_timezone(), self.UTC)

    def test_anon_process_request(self):
        self.request.user = auth.get_user(Client())
        self.assertTrue(self.request.user.is_anonymous())
        self.assertFalse(self.request.user.is_authenticated())
        self.assertEqual(timezone.get_current_timezone(), self.UTC)

        self.assertEqual(self.tzm.process_request(self.request), None)
        self.assertEqual(timezone.get_current_timezone(), self.UTC)

    def test_no_tz_process_request(self):
        self.request.user = auth.get_user_model().objects.create(username='new_user')
        self.assertFalse(self.request.user.is_anonymous())
        self.assertTrue(self.request.user.is_authenticated())
        self.assertEqual(self.request.user.time_zone, None)

        self.assertEqual(timezone.get_current_timezone(), self.UTC)
        self.assertEqual(self.tzm.process_request(self.request), None)
        self.assertEqual(timezone.get_current_timezone(), self.UTC)

    def test_custom_tz_process_request(self):
        self.request.user = auth.get_user_model().objects.create(username='new_user', time_zone='Australia/Adelaide')
        self.assertFalse(self.request.user.is_anonymous())
        self.assertTrue(self.request.user.is_authenticated())
        self.assertEqual(timezone.get_current_timezone(), self.UTC)

        self.assertEqual(self.tzm.process_request(self.request), None)
        self.assertEqual(timezone.get_current_timezone(), pytz.timezone(self.request.user.time_zone))


class WsgiLogErrorsTest(TestCase):

    def setUp(self):
        super(WsgiLogErrorsTest, self).setUp()
        self.wle = WsgiLogErrors()
        self.request = Mock()
        self.request.META = {'wsgi.errors': StringIO()}
        self.exception = Exception('test exception', 'abc')
        self.exception404 = Http404('test 404', 'abc')
        self.exception403 = PermissionDenied('test 403', 'abc')

    def test_process_exception(self):
        self.assertEqual(self.request.META['wsgi.errors'].getvalue(), '')
        response = self.wle.process_exception(self.request, self.exception)
        self.assertEqual(response, None)
        self.assertRegexpMatches(
            self.request.META['wsgi.errors'].getvalue(),
            "^EXCEPTION raised serving: <Mock name='mock\.build_absolute_uri\(\)' id='\d+'>"
        )

    def test_skip_403(self):
        self.assertEqual(self.request.META['wsgi.errors'].getvalue(), '')
        response = self.wle.process_exception(self.request, self.exception403)
        self.assertEqual(response, None)
        self.assertEqual(self.request.META['wsgi.errors'].getvalue(), '')

    def test_skip_404(self):
        self.assertEqual(self.request.META['wsgi.errors'].getvalue(), '')
        response = self.wle.process_exception(self.request, self.exception404)
        self.assertEqual(response, None)
        self.assertEqual(self.request.META['wsgi.errors'].getvalue(), '')


class P3PMiddlewareTest(TestCase):

    def setUp(self):
        super(P3PMiddlewareTest, self).setUp()
        self.p3p = P3PMiddleware()
        self.request = Mock()
        self.response = HttpResponse()

    def test_response_header_present(self):
        self.p3p.process_response(self.request, self.response)
        self.assertEqual(self.response[settings.P3P_HEADER_KEY], settings.P3P_HEADER_VALUE)
