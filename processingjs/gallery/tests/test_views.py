from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse


class ShareViewTest(TestCase):

    def test_share_view(self):
        client = Client()
        share_path = reverse('share')
        response = client.get(share_path)
        self.assertEqual(response.status_code, 200)
