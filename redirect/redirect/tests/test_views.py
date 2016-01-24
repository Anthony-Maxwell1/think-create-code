from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

class ShareViewTests(TestCase):
    '''ShareView tests'''

    def test_share(self):
        client = Client()
        url = reverse('home')
        response = client.get(url)


