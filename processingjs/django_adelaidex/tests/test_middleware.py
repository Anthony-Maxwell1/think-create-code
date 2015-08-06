from django.test import TestCase
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.http import Http404, HttpResponse
from exceptions import Exception
from StringIO import StringIO
from mock import Mock

from django_adelaidex.test import UserSetUp
from django_adelaidex.middleware import WsgiLogErrors, P3PMiddleware

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
