from django.test import TestCase, LiveServerTestCase
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from selenium.webdriver.firefox.webdriver import WebDriver
from pyvirtualdisplay import Display
import os, time, re

from artwork.models import Artwork


class ArtworkTests(TestCase):
    """Artwork model tests."""

    def test_str(self):
        
        artwork = Artwork(title='Empty code', code='// code goes here')

        self.assertEquals(
            str(artwork),
            'Empty code'
        )


class ArtworkListTests(TestCase):
    """Artwork list view tests."""

    def setUp(self):
        self.user = get_user_model().objects.create(username='some_user')


    def test_artwork_in_the_context(self):
        
        client = Client()
        response = client.get('/')

        self.assertEquals(list(response.context['object_list']), [])

        Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        response = client.get('/')
        self.assertEquals(response.context['object_list'].count(), 1)


class ArtworkViewTests(TestCase):
    """Artwork view tests."""

    def setUp(self):
        self.user = get_user_model().objects.create(username='some_user')


    def test_artwork_in_the_context(self):
        
        client = Client()

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        response = client.get(reverse('artwork-view', kwargs={'pk':artwork.id}))
        self.assertEquals(response.context['object'].title, artwork.title)
        self.assertEquals(response.context['object'].code, artwork.code)


class ArtworkDeleteTests(TestCase):
    """Artwork delete view tests."""

    def setUp(self):
        self.user = get_user_model().objects.create(username='some_user')

    def test_artwork_in_the_context(self):
        
        client = Client()

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        response = client.get(reverse('artwork-delete', kwargs={'pk':artwork.id}))
        self.assertEquals(response.context['object'].title, artwork.title)
        self.assertEquals(response.context['object'].code, artwork.code)



class ArtworkListIntegrationTests(LiveServerTestCase):
    """Run live server integration tests.  Requires running xvfb service."""

    @classmethod
    def setUpClass(cls):
        # /etc/init.d/xfvb running on port 0
        os.environ['DISPLAY'] = ':0'
        os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = '0.0.0.0:8080'
        cls.selenium = WebDriver()
        cls.display = Display(visible=0, size=(800, 600))
        cls.display.start()
        super(ArtworkListIntegrationTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        cls.display.stop()
        super(ArtworkListIntegrationTests, cls).tearDownClass()

    def setUp(self):
        self.user = get_user_model().objects.create(username='some_user')


    def test_artwork_listed(self):

        Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)

        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id('list-artwork-add')
        )

    def test_add_artwork_linked(self):

        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.assertIsNotNone(
            self.selenium.find_element_by_id('list-artwork-add')
        )

    def test_add_artwork(self):

        source = self.selenium.get('%s%s' % (self.live_server_url, reverse('artwork-add')))
        self.selenium.find_element_by_id('id_title').send_keys('test submission')
        self.selenium.find_element_by_id('id_code').send_keys('// code goes here')

        select_author = self.selenium.find_element_by_id('id_author')
        for option in select_author.find_elements_by_tag_name('option'):
            if option.text == self.user.username:
                option.click()
                break
        
        self.selenium.find_element_by_id('save_artwork').click()

        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )


    def test_add_artwork_cancel(self):

        source = self.selenium.get('%s%s' % (self.live_server_url, reverse('artwork-add')))

        self.selenium.find_element_by_id('id_title').send_keys('do not submit')
        self.selenium.find_element_by_id('id_code').send_keys('// code goes here')

        select_author = self.selenium.find_element_by_id('id_author')
        for option in select_author.find_elements_by_tag_name('option'):
            if option.text == self.user.username:
                option.click()
                break

        self.selenium.find_element_by_id('save_cancel').click()
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )

    def test_delete_artwork(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        source = self.selenium.get('%s%s' % (self.live_server_url, reverse('artwork-delete', kwargs={'pk':artwork.id})))

        self.selenium.find_element_by_id('artwork_delete').click()
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            0
        )
        
    def test_delete_artwork_cancel(self):

        artwork = Artwork.objects.create(title='Title bar', code='// code goes here', author=self.user)
        source = self.selenium.get('%s%s' % (self.live_server_url, reverse('artwork-delete', kwargs={'pk':artwork.id})))

        self.selenium.find_element_by_id('artwork_do_not_delete').click()
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.artwork')),
            1
        )
        
