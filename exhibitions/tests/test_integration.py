from django.core.urlresolvers import reverse

from exhibitions.models import Exhibition
from gallery.tests import SeleniumTestCase


class ExhibitionListIntegrationTests(SeleniumTestCase):

    def setUp(self):
        super(ExhibitionListIntegrationTests, self).setUp()
        self.list_url = '%s%s' % (self.live_server_url, reverse('exhibition-list'))

    def test_empty_list(self):

        self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            0
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id('list-add-button')
        )


    def test_exhibition_listed(self):

        Exhibition.objects.create(title='New Exhibition', description='goes here', author=self.user)

        self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id('list-add-button')
        )

    def test_exhibition_listed_descr_truncated(self):

        Exhibition.objects.create(title='New Exhibition', description='x' * 200, author=self.user)

        self.selenium.get(self.list_url)
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.exhibition-description').text,
            '%s...' % ('x' * 97)
        )


class ExhibitionViewIntegrationTests(SeleniumTestCase):

    def test_view_not_found(self):

        self.selenium.get('%s%s' % (self.live_server_url, reverse('exhibition-view', kwargs={'pk': 1})))
        self.assertEqual(
            self.selenium.find_element_by_css_selector('p').text,
            'The requested URL /exhibitions/1/ was not found on this server.'
        )


    def test_view(self):

        exhibition = Exhibition.objects.create(title='New Exhibition', description='goes here', author=self.user)

        self.selenium.get('%s%s' % (self.live_server_url, reverse('exhibition-view', kwargs={'pk': exhibition.id})))
        self.assertEqual(
            len(self.selenium.find_elements_by_id('exhibition-view-content')),
            1
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.exhibition-title').text,
            exhibition.title
        )
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.exhibition-description').text,
            exhibition.description
        )


class ExhibitionCreateIntegrationTests(SeleniumTestCase):

    def test_add_exhibition(self):

        add_path = reverse('exhibition-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form
        self.assertLogin(add_path)

        # login form redirects to add form
        self.selenium.find_element_by_id('id_title').send_keys('test submission')
        self.selenium.find_element_by_id('id_description').send_keys('description goes here')

        self.selenium.find_element_by_id('save_exhibition').click()

        # add action redirects to view url
        view_path = reverse('exhibition-view', kwargs={'pk': 1})
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, view_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )

    def test_add_exhibition_cancel(self):

        add_path = reverse('exhibition-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form
        self.assertLogin(add_path)

        # login form redirects to add form
        self.selenium.find_element_by_id('id_title').send_keys('do not submit')
        self.selenium.find_element_by_id('id_description').send_keys('description goes here')

        self.selenium.find_element_by_id('save_cancel').click()

        # cancel action redirects to list url
        list_path = reverse('exhibition-list')
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            0
        )


class ExhibitionEditIntegrationTests(SeleniumTestCase):

    def test_edit_exhibition(self):

        exhibition = Exhibition.objects.create(title='Title bar', description='description goes here', author=self.user)

        edit_path = reverse('exhibition-edit', kwargs={'pk': exhibition.id})
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))

        # edit redirects to login form
        self.assertLogin(edit_path)

        # Update the title text
        self.selenium.find_element_by_id('id_title').clear()
        self.selenium.find_element_by_id('id_title').send_keys('updated title')

        # Click Save
        self.selenium.find_element_by_id('save_exhibition').click()

        # save returns us to the view page
        view_path = reverse('exhibition-view', kwargs={'pk': exhibition.id})
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, view_path))

        # ensure the save was made
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.exhibition-title').text,
            'updated title'
        )

    def test_edit_exhibition_cancel(self):

        exhibition = Exhibition.objects.create(title='Title bar', description='description goes here', author=self.user)

        edit_path = reverse('exhibition-edit', kwargs={'pk': exhibition.id})
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))

        # edit redirects to login form
        self.assertLogin(edit_path)

        # Update the title text
        self.selenium.find_element_by_id('id_title').clear()
        self.selenium.find_element_by_id('id_title').send_keys('updated title')

        # Click cancel
        self.selenium.find_element_by_id('save_cancel').click()

        # Cancel returns us to the list page
        list_path = reverse('exhibition-list')
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))

        # view the work to ensure edit was canceled
        view_path = reverse('exhibition-view', kwargs={'pk': exhibition.id})
        self.selenium.get('%s%s' % (self.live_server_url, view_path))
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.exhibition-title').text,
            'Title bar'
        )


class ExhibitionDeleteIntegrationTests(SeleniumTestCase):

    def test_delete_exhibition(self):

        exhibition = Exhibition.objects.create(title='Title bar', description='description goes here', author=self.user)
        delete_path = reverse('exhibition-delete', kwargs={'pk':exhibition.id})
        self.selenium.get('%s%s' % (self.live_server_url, delete_path))

        # delete redirects to login form
        self.assertLogin(delete_path)

        # login form redirects to delete form
        self.selenium.find_element_by_id('exhibition_delete').click()

        # delete action redirects to list url
        list_path = reverse('exhibition-list')
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            0
        )
        
    def test_delete_exhibition_cancel(self):

        exhibition = Exhibition.objects.create(title='Title bar', description='description goes here', author=self.user)
        delete_path = reverse('exhibition-delete', kwargs={'pk':exhibition.id})
        self.selenium.get('%s%s' % (self.live_server_url, delete_path))

        # delete redirects to login form
        self.assertLogin(delete_path)

        # login form redirects to delete form
        self.selenium.find_element_by_id('exhibition_do_not_delete').click()

        # delete action redirects to list url
        list_path = reverse('exhibition-list')
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )

