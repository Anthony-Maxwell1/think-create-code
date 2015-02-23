from django.test import TestCase
from django.test.client import Client
from django.conf import settings


class AnalyticsContextTest(TestCase):

    def setUp(self):
        self.allow_analytics = settings.ALLOW_ANALYTICS

    def tearDown(self):
        settings.ALLOW_ANALYTICS = self.allow_analytics

    def test_allow_analytics(self):

        settings.ALLOW_ANALYTICS = True
        client = Client()
        response = client.get('/')
        self.assertTrue(response.context['ALLOW_ANALYTICS'])

    def test_disallow_analytics(self):

        settings.ALLOW_ANALYTICS = False
        client = Client()
        response = client.get('/')
        self.assertFalse(response.context['ALLOW_ANALYTICS'])
