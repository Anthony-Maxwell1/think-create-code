from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from selenium.common.exceptions import NoSuchElementException
from django.utils import timezone
from datetime import timedelta

from exhibitions.models import Exhibition
from uofa.test import SeleniumTestCase, wait_for_page_load


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
        # public doesn't see add button
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('list-add-button')
        )

    def test_empty_list_student(self):

        self.performLogin(user='student')
        self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            0
        )
        # students doesn't see add button
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('list-add-button')
        )

    def test_empty_list_staff(self):

        self.performLogin(user='staff')
        self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            0
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id('list-add-button')
        )

    def test_empty_list_super(self):

        self.performLogin(user='super')
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
        # public don't see add button
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('list-add-button')
        )

    def test_exhibition_listed_descr_truncated(self):

        Exhibition.objects.create(title='New Exhibition', description='x' * 200, author=self.user)

        self.selenium.get(self.list_url)
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.exhibition-description').text,
            '%s...' % ('x' * 97)
        )

    def test_exhibition_listed_student(self):

        Exhibition.objects.create(title='New Exhibition', description='goes here', author=self.user)
        self.performLogin(user='student')

        self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        # students don't see add button
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('list-add-button')
        )

    def test_exhibition_listed_staff(self):

        Exhibition.objects.create(title='New Exhibition', description='goes here', author=self.user)
        self.performLogin(user='staff')

        self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id('list-add-button')
        )

    def test_exhibition_listed_super(self):

        Exhibition.objects.create(title='New Exhibition', description='goes here', author=self.user)
        self.performLogin(user='super')

        self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id('list-add-button')
        )

    def test_list_before_release_date(self):
        
        # Public can only see exhibitions whose release date has past
        now = timezone.now()
        yesterday = Exhibition.objects.create(
            title='Exhibition One',
            description='description goes here',
            released_at = now + timedelta(hours=-24),
            author=self.user)
        today = Exhibition.objects.create(
            title='Exhibition Two',
            description='description goes here',
            released_at = now,
            author=self.user)
        tomorrow = Exhibition.objects.create(
            title='Exhibition Three',
            description='description goes here',
            released_at = now + timedelta(hours=24),
            author=self.user)

        self.selenium.get(self.list_url)
        title_items = self.selenium.find_elements_by_css_selector('.exhibition-title')
        self.assertEqual(
            len(title_items),
            2
        )
        self.assertEqual(title_items[0].text, today.title)
        self.assertEqual(title_items[1].text, yesterday.title)

    def test_staff_list_before_release_date(self):
        
        # Staff can see all exhibitions
        now = timezone.now()
        yesterday = Exhibition.objects.create(
            title='Exhibition One',
            description='description goes here',
            released_at = now + timedelta(hours=-24),
            author=self.user)
        today = Exhibition.objects.create(
            title='Exhibition Two',
            description='description goes here',
            released_at = now,
            author=self.user)
        tomorrow = Exhibition.objects.create(
            title='Exhibition Three',
            description='description goes here',
            released_at = now + timedelta(hours=24),
            author=self.user)

        self.performLogin(user='staff')
        self.selenium.get(self.list_url)

        title_items = self.selenium.find_elements_by_css_selector('.exhibition-title')
        self.assertEqual(
            len(title_items),
            3
        )
        self.assertEqual(title_items[0].text, tomorrow.title)
        self.assertEqual(title_items[1].text, today.title)
        self.assertEqual(title_items[2].text, yesterday.title)

    def test_super_list_before_release_date(self):
        
        # Superusers can see all exhibitions
        now = timezone.now()
        yesterday = Exhibition.objects.create(
            title='Exhibition One',
            description='description goes here',
            released_at = now + timedelta(hours=-24),
            author=self.user)
        today = Exhibition.objects.create(
            title='Exhibition Two',
            description='description goes here',
            released_at = now,
            author=self.user)
        tomorrow = Exhibition.objects.create(
            title='Exhibition Three',
            description='description goes here',
            released_at = now + timedelta(hours=24),
            author=self.user)

        self.performLogin(user='super')
        self.selenium.get(self.list_url)

        title_items = self.selenium.find_elements_by_css_selector('.exhibition-title')
        self.assertEqual(
            len(title_items),
            3
        )
        self.assertEqual(title_items[0].text, tomorrow.title)
        self.assertEqual(title_items[1].text, today.title)
        self.assertEqual(title_items[2].text, yesterday.title)


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
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('EDIT')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('DELETE')
        )

    def test_view_student(self):

        exhibition = Exhibition.objects.create(title='New Exhibition', description='goes here', author=self.user)
        self.performLogin('student')

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
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('EDIT')
        )
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_link_text, ('DELETE')
        )

    def test_view_staff(self):

        exhibition = Exhibition.objects.create(title='New Exhibition', description='goes here', author=self.user)
        self.performLogin(user='staff')

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
        edit_url = '%s%s' % (self.live_server_url, reverse('exhibition-edit', kwargs={'pk': exhibition.id}))
        self.assertEqual(
            self.selenium.find_element_by_link_text('EDIT').get_attribute('href'),
            edit_url
        )
        delete_url = '%s%s' % (self.live_server_url, reverse('exhibition-delete', kwargs={'pk': exhibition.id}))
        self.assertEqual(
            self.selenium.find_element_by_link_text('DELETE').get_attribute('href'),
            delete_url
        )

    def test_view_super(self):

        exhibition = Exhibition.objects.create(title='New Exhibition', description='goes here', author=self.user)
        self.performLogin(user='super')

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
        edit_url = '%s%s' % (self.live_server_url, reverse('exhibition-edit', kwargs={'pk': exhibition.id}))
        self.assertEqual(
            self.selenium.find_element_by_link_text('EDIT').get_attribute('href'),
            edit_url
        )
        delete_url = '%s%s' % (self.live_server_url, reverse('exhibition-delete', kwargs={'pk': exhibition.id}))
        self.assertEqual(
            self.selenium.find_element_by_link_text('DELETE').get_attribute('href'),
            delete_url
        )

    def test_view_before_release_date(self):

        now = timezone.now()
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = now + timedelta(hours=24),
            author=self.user)

        view_url = '%s%s' % (self.live_server_url, reverse('exhibition-view', kwargs={'pk': exhibition.id}))
        self.selenium.get(view_url)
        self.assertRegexpMatches(self.selenium.page_source, r'403 Forbidden')

    def test_staff_view_before_release_date(self):

        now = timezone.now()
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = now + timedelta(hours=24),
            author=self.user)

        view_url = '%s%s' % (self.live_server_url, reverse('exhibition-view', kwargs={'pk': exhibition.id}))
        self.performLogin(user='staff')
        self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('exhibition-view-content')),
            1
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_css_selector('.not-available')
        )

    def test_super_view_before_release_date(self):

        now = timezone.now()
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = now + timedelta(hours=24),
            author=self.user)

        view_url = '%s%s' % (self.live_server_url, reverse('exhibition-view', kwargs={'pk': exhibition.id}))
        self.performLogin(user='staff')
        self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('exhibition-view-content')),
            1
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_css_selector('.not-available')
        )


class ExhibitionCreateIntegrationTests(SeleniumTestCase):

    def test_staff_add_exhibition(self):

        add_path = reverse('exhibition-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form
        self.assertLogin(add_path, user='staff')

        # login form redirects to add form
        self.selenium.find_element_by_id('id_title').send_keys('test submission')
        self.selenium.find_element_by_id('id_description').send_keys('description goes here')

        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_exhibition').click()

        # add action redirects to view url
        view_path = reverse('exhibition-view', kwargs={'pk': 1})
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, view_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )

    def test_staff_add_exhibition_cancel(self):

        add_path = reverse('exhibition-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form
        self.assertLogin(add_path, user='staff')

        # login form redirects to add form
        self.selenium.find_element_by_id('id_title').send_keys('do not submit')
        self.selenium.find_element_by_id('id_description').send_keys('description goes here')

        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_cancel').click()

        # cancel action redirects to list url
        list_path = reverse('exhibition-list')
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            0
        )

    def test_students_cannot_add_exhibition(self):

        add_path = reverse('exhibition-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form, which redirects to list page
        list_path = reverse('exhibition-list')
        self.assertLoginRedirects(add_path, redirect_path=list_path)


class ExhibitionEditIntegrationTests(SeleniumTestCase):

    def test_staff_edit_exhibition(self):

        exhibition = Exhibition.objects.create(title='Title bar', description='description goes here', author=self.staff_user)

        edit_path = reverse('exhibition-edit', kwargs={'pk': exhibition.id})
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))

        # edit redirects to login form
        self.assertLogin(edit_path, user='staff')

        # Update the title text
        self.selenium.find_element_by_id('id_title').clear()
        self.selenium.find_element_by_id('id_title').send_keys('updated title')

        # Click Save
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_exhibition').click()

        # save returns us to the view page
        view_path = reverse('exhibition-view', kwargs={'pk': exhibition.id})
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, view_path))

        # ensure the save was made
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.exhibition-title').text,
            'updated title'
        )

    def test_staff_edit_any_exhibition(self):

        otherUser = get_user_model().objects.create(username='otherStaff', is_staff=True)
        exhibition = Exhibition.objects.create(title='Title bar', description='description goes here', author=otherUser)

        edit_path = reverse('exhibition-edit', kwargs={'pk': exhibition.id})
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))

        # edit redirects to login form
        self.assertLogin(edit_path, user='staff')

        # Update the title text
        self.selenium.find_element_by_id('id_title').clear()
        self.selenium.find_element_by_id('id_title').send_keys('updated title')

        # Click Save
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_exhibition').click()

        # save returns us to the view page
        view_path = reverse('exhibition-view', kwargs={'pk': exhibition.id})
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, view_path))

        # ensure the save was made
        self.assertEqual(
            self.selenium.find_element_by_css_selector('.exhibition-title').text,
            'updated title'
        )

    def test_staff_edit_exhibition_cancel(self):

        exhibition = Exhibition.objects.create(title='Title bar', description='description goes here', author=self.staff_user)

        edit_path = reverse('exhibition-edit', kwargs={'pk': exhibition.id})
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))

        # edit redirects to login form
        self.assertLogin(edit_path, user='staff')

        # Update the title text
        self.selenium.find_element_by_id('id_title').clear()
        self.selenium.find_element_by_id('id_title').send_keys('updated title')

        # Click cancel
        with wait_for_page_load(self.selenium):
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

    def test_students_cannot_edit_exhibition(self):

        exhibition = Exhibition.objects.create(title='Title bar', description='description goes here', author=self.staff_user)

        edit_path = reverse('exhibition-edit', kwargs={'pk': exhibition.id})
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))

        # add redirects to login form, which redirects to list page
        list_path = reverse('exhibition-list')
        self.assertLoginRedirects(edit_path, redirect_path=list_path)


class ExhibitionDeleteIntegrationTests(SeleniumTestCase):

    def test_staff_delete_exhibition(self):

        exhibition = Exhibition.objects.create(title='Title bar', description='description goes here', author=self.staff_user)
        delete_path = reverse('exhibition-delete', kwargs={'pk':exhibition.id})
        self.selenium.get('%s%s' % (self.live_server_url, delete_path))

        # delete redirects to login form
        self.assertLogin(delete_path, user='staff')

        # login form redirects to delete form
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('exhibition_delete').click()

        # delete action redirects to list url
        list_path = reverse('exhibition-list')
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            0
        )
        
    def test_staff_delete_any_exhibition(self):

        otherUser = get_user_model().objects.create(username='otherStaff', is_staff=True)
        exhibition = Exhibition.objects.create(title='Title bar', description='description goes here', author=otherUser)

        delete_path = reverse('exhibition-delete', kwargs={'pk':exhibition.id})
        self.selenium.get('%s%s' % (self.live_server_url, delete_path))

        # delete redirects to login form
        self.assertLogin(delete_path, user='staff')

        # login form redirects to delete form
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('exhibition_delete').click()

        # delete action redirects to list url
        list_path = reverse('exhibition-list')
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            0
        )
        
    def test_staff_delete_exhibition_cancel(self):

        exhibition = Exhibition.objects.create(title='Title bar', description='description goes here', author=self.staff_user)
        delete_path = reverse('exhibition-delete', kwargs={'pk':exhibition.id})
        self.selenium.get('%s%s' % (self.live_server_url, delete_path))

        # delete redirects to login form
        self.assertLogin(delete_path, user='staff')

        # login form redirects to delete form
        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('exhibition_do_not_delete').click()

        # delete action redirects to list url
        list_path = reverse('exhibition-list')
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )

    def test_students_cannot_delete_exhibition(self):

        exhibition = Exhibition.objects.create(title='Title bar', description='description goes here', author=self.user)
        delete_path = reverse('exhibition-delete', kwargs={'pk':exhibition.id})
        self.selenium.get('%s%s' % (self.live_server_url, delete_path))

        # delete redirects to login form, which redirects to list page
        list_path = reverse('exhibition-list')
        self.assertLoginRedirects(delete_path, redirect_path=list_path)
