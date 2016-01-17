from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from selenium.common.exceptions import NoSuchElementException
from django.utils import timezone
from datetime import timedelta
import os, os.path
import re

from exhibitions.models import Exhibition
from django_adelaidex.lti.models import Cohort
from django_adelaidex.util.test import SeleniumTestCase, wait_for_page_load
from exhibitions.tests.test_views import CohortMixin, ExhibitionCohortMixin


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
            self.selenium.find_element_by_id, ('exhibition-add')
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
            self.selenium.find_element_by_id, ('exhibition-add')
        )

    def test_empty_list_staff(self):

        self.performLogin(user='staff')
        self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            0
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id('exhibition-add')
        )

    def test_empty_list_super(self):

        self.performLogin(user='super')
        self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            0
        )
        self.assertIsNotNone(
            self.selenium.find_element_by_id('exhibition-add')
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
            self.selenium.find_element_by_id, ('exhibition-add')
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
            self.selenium.find_element_by_id, ('exhibition-add')
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
            self.selenium.find_element_by_id('exhibition-add')
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
            self.selenium.find_element_by_id('exhibition-add')
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

    def test_list_pk_list(self):
        
        # Create three exhibitions
        now = timezone.now()
        exhibition1 = Exhibition.objects.create(
            title='Exhibition One',
            description='description goes here',
            released_at = now,
            author=self.user)

        exhibition2 = Exhibition.objects.create(
            title='Exhibition Two',
            description='description goes here',
            released_at = now,
            author=self.user)

        exhibition3 = Exhibition.objects.create(
            title='Exhibition Three',
            description='description goes here',
            released_at = now,
            author=self.user)

        pk_list = []
        list_url = '%s%s' % (self.live_server_url, reverse('exhibition-list', 
                        kwargs={'pk_list': ','.join(map(str,pk_list))}))
        self.selenium.get(list_url)
        title_items = self.selenium.find_elements_by_css_selector('.exhibition-title')
        self.assertEqual(len(title_items), 3)
        self.assertEqual(title_items[0].text, exhibition1.title)
        self.assertEqual(title_items[1].text, exhibition2.title)
        self.assertEqual(title_items[2].text, exhibition3.title)

        pk_list = [exhibition1.id, exhibition3.id]
        list_url = '%s%s' % (self.live_server_url, reverse('exhibition-list', 
                        kwargs={'pk_list': ','.join(map(str,pk_list))}))
        self.selenium.get(list_url)
        title_items = self.selenium.find_elements_by_css_selector('.exhibition-title')
        self.assertEqual(len(title_items), 2)
        self.assertEqual(title_items[0].text, exhibition1.title)
        self.assertEqual(title_items[1].text, exhibition3.title)

        pk_list = [exhibition1.id, exhibition2.id]
        list_url = '%s%s' % (self.live_server_url, reverse('exhibition-list', 
                        kwargs={'pk_list': ','.join(map(str,pk_list))}))
        self.selenium.get(list_url)
        title_items = self.selenium.find_elements_by_css_selector('.exhibition-title')
        self.assertEqual(len(title_items), 2)
        self.assertEqual(title_items[0].text, exhibition1.title)
        self.assertEqual(title_items[1].text, exhibition2.title)

        pk_list = [exhibition1.id, exhibition2.id, exhibition3.id]
        list_url = '%s%s' % (self.live_server_url, reverse('exhibition-list', 
                        kwargs={'pk_list': ','.join(map(str,pk_list))}))
        self.selenium.get(list_url)
        title_items = self.selenium.find_elements_by_css_selector('.exhibition-title')
        self.assertEqual(len(title_items), 3)
        self.assertEqual(title_items[0].text, exhibition1.title)
        self.assertEqual(title_items[1].text, exhibition2.title)
        self.assertEqual(title_items[2].text, exhibition3.title)


class ExhibitionListCohortIntegrationTests(ExhibitionCohortMixin, SeleniumTestCase):

    def setUp(self):
        super(ExhibitionListCohortIntegrationTests, self).setUp()
        self.list_url = '%s%s' % (self.live_server_url, reverse('exhibition-list'))

    def test_public_list(self):

        # Public sees the no-cohort and default cohort exhibitions
        self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            2
        )
        title_items = self.selenium.find_elements_by_css_selector('.exhibition-title')
        self.assertEqual(
            len(title_items),
            2
        )
        self.assertEqual(title_items[0].text, self.exhibition_no_cohort.title)
        self.assertEqual(title_items[1].text, self.exhibition_cohort1.title)

        # public doesn't see add button
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('exhibition-add')
        )

    def test_student_list(self):

        # Student (with no cohort) sees the no-cohort and default cohort exhibitions
        self.assertIsNone(self.user.cohort)
        self.performLogin(user='student')
        self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            2
        )
        title_items = self.selenium.find_elements_by_css_selector('.exhibition-title')
        self.assertEqual(
            len(title_items),
            2
        )
        self.assertEqual(title_items[0].text, self.exhibition_no_cohort.title)
        self.assertEqual(title_items[1].text, self.exhibition_cohort1.title)

        # student doesn't see add button
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('exhibition-add')
        )

        # Move student into cohort1, and she sees no-cohort and cohort2
        self.user.cohort = self.cohort1
        self.user.save()
        self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            2
        )
        title_items = self.selenium.find_elements_by_css_selector('.exhibition-title')
        self.assertEqual(
            len(title_items),
            2
        )
        self.assertEqual(title_items[0].text, self.exhibition_no_cohort.title)
        self.assertEqual(title_items[1].text, self.exhibition_cohort1.title)

        # student doesn't see add button
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('exhibition-add')
        )

        # Move student into cohort2, and she sees no-cohort and cohort2
        self.user.cohort = self.cohort2
        self.user.save()
        self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            2
        )
        title_items = self.selenium.find_elements_by_css_selector('.exhibition-title')
        self.assertEqual(
            len(title_items),
            2
        )
        self.assertEqual(title_items[0].text, self.exhibition_no_cohort.title)
        self.assertEqual(title_items[1].text, self.exhibition_cohort2.title)

        # student doesn't see add button
        self.assertRaises(
            NoSuchElementException,
            self.selenium.find_element_by_id, ('exhibition-add')
        )

    def test_staff_list(self):

        # Staff (with no cohort) sees the no-cohort and default cohort exhibitions
        self.assertIsNone(self.staff_user.cohort)
        self.performLogin(user='staff')
        self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            2
        )
        title_items = self.selenium.find_elements_by_css_selector('.exhibition-title')
        self.assertEqual(
            len(title_items),
            2
        )
        self.assertEqual(title_items[0].text, self.exhibition_no_cohort.title)
        self.assertEqual(title_items[1].text, self.exhibition_cohort1.title)

        # staff see add button
        self.assertIsNotNone(
            self.selenium.find_element_by_id('exhibition-add')
        )

        # Move staff into cohort1, and she sees no-cohort and cohort2
        self.staff_user.cohort = self.cohort1
        self.staff_user.save()
        self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            2
        )
        title_items = self.selenium.find_elements_by_css_selector('.exhibition-title')
        self.assertEqual(
            len(title_items),
            2
        )
        self.assertEqual(title_items[0].text, self.exhibition_no_cohort.title)
        self.assertEqual(title_items[1].text, self.exhibition_cohort1.title)

        # staff see add button
        self.assertIsNotNone(
            self.selenium.find_element_by_id('exhibition-add')
        )

        # Move staff into cohort2, and she sees no-cohort and cohort2
        self.staff_user.cohort = self.cohort2
        self.staff_user.save()
        self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            2
        )

        title_items = self.selenium.find_elements_by_css_selector('.exhibition-title')
        self.assertEqual(
            len(title_items),
            2
        )
        self.assertEqual(title_items[0].text, self.exhibition_no_cohort.title)
        self.assertEqual(title_items[1].text, self.exhibition_cohort2.title)

        # staff see add button
        self.assertIsNotNone(
            self.selenium.find_element_by_id('exhibition-add')
        )

    def test_super_list(self):

        # Superusers (with no cohort) see the full list of exhibitions
        self.assertIsNone(self.super_user.cohort)
        self.performLogin(user='super')
        self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            3
        )
        title_items = self.selenium.find_elements_by_css_selector('.exhibition-title')
        self.assertEqual(
            len(title_items),
            3
        )
        self.assertEqual(title_items[0].text, self.exhibition_no_cohort.title)
        self.assertEqual(title_items[1].text, self.exhibition_cohort1.title)
        self.assertEqual(title_items[2].text, self.exhibition_cohort2.title)

        # superusers see add button
        self.assertIsNotNone(
            self.selenium.find_element_by_id('exhibition-add')
        )

        # Move superuser into cohort1, and she still sees all the exhibitions
        self.super_user.cohort = self.cohort1
        self.super_user.save()
        self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            3
        )
        title_items = self.selenium.find_elements_by_css_selector('.exhibition-title')
        self.assertEqual(
            len(title_items),
            3
        )
        self.assertEqual(title_items[0].text, self.exhibition_no_cohort.title)
        self.assertEqual(title_items[1].text, self.exhibition_cohort1.title)
        self.assertEqual(title_items[2].text, self.exhibition_cohort2.title)

        # superuser see add button
        self.assertIsNotNone(
            self.selenium.find_element_by_id('exhibition-add')
        )

        # Move superuser into cohort2, and she still sees all the exhibitions
        self.super_user.cohort = self.cohort2
        self.super_user.save()
        self.selenium.get(self.list_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            3
        )
        title_items = self.selenium.find_elements_by_css_selector('.exhibition-title')
        self.assertEqual(
            len(title_items),
            3
        )
        self.assertEqual(title_items[0].text, self.exhibition_no_cohort.title)
        self.assertEqual(title_items[1].text, self.exhibition_cohort1.title)
        self.assertEqual(title_items[2].text, self.exhibition_cohort2.title)

        # superuser see add button
        self.assertIsNotNone(
            self.selenium.find_element_by_id('exhibition-add')
        )


class ExhibitionViewIntegrationTests(SeleniumTestCase):

    def test_view_not_found(self):

        self.selenium.get('%s%s' % (self.live_server_url, reverse('exhibition-view', kwargs={'pk': 1})))
        self.assertEqual(
            self.selenium.find_element_by_css_selector('p').text,
            'The page you were looking for has been moved, deleted, or does not exist.'
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


class ExhibitionViewCohortIntegrationTests(ExhibitionCohortMixin, SeleniumTestCase):

    def assert_can_view(self, exhibition, can_edit=False):
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

        if can_edit:
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
        else:
            self.assertRaises(
                NoSuchElementException,
                self.selenium.find_element_by_link_text, ('EDIT')
            )
            self.assertRaises(
                NoSuchElementException,
                self.selenium.find_element_by_link_text, ('DELETE')
            )

    def assert_403(self, exhibition):
        self.selenium.get('%s%s' % (self.live_server_url, reverse('exhibition-view', kwargs={'pk': exhibition.id})))
        self.assertEqual(
            len(self.selenium.find_elements_by_id('exhibition-view-content')),
            0
        )
        error_403 = self.selenium.find_element_by_tag_name('h1')
        self.assertEqual(
            error_403.text, '403 Forbidden'
        )

    def test_public_view(self):

        # Public can see no-cohort and default cohort exhibitions
        exhibition = self.exhibition_no_cohort
        self.assert_can_view(self.exhibition_no_cohort)
        self.assert_can_view(self.exhibition_cohort1)
        self.assert_403(self.exhibition_cohort2)

    def test_view_student(self):

        # Students can see no-cohort and default cohort exhibitions
        self.performLogin(user='student')
        self.assert_can_view(self.exhibition_no_cohort)
        self.assert_can_view(self.exhibition_cohort1)
        self.assert_403(self.exhibition_cohort2)

        # Move the student into cohort 1, no change to exhibitions viewed
        self.user.cohort = self.cohort1
        self.user.save()
        self.assert_can_view(self.exhibition_no_cohort)
        self.assert_can_view(self.exhibition_cohort1)
        self.assert_403(self.exhibition_cohort2)

        # Move the student into cohort 2, and she can't see cohort1 anymore, but can see cohort2
        self.user.cohort = self.cohort2
        self.user.save()
        self.assert_can_view(self.exhibition_no_cohort)
        self.assert_403(self.exhibition_cohort1)
        self.assert_can_view(self.exhibition_cohort2)

    def test_view_staff(self):

        # Staff can see all exhibitions
        self.performLogin(user='staff')
        self.assert_can_view(self.exhibition_no_cohort, can_edit=True)
        self.assert_can_view(self.exhibition_cohort1, can_edit=True)
        self.assert_can_view(self.exhibition_cohort2, can_edit=True)

        # Move the staff user into cohort 1, no change to exhibitions viewed
        self.staff_user.cohort = self.cohort1
        self.staff_user.save()
        self.assert_can_view(self.exhibition_no_cohort, can_edit=True)
        self.assert_can_view(self.exhibition_cohort1, can_edit=True)
        self.assert_can_view(self.exhibition_cohort2, can_edit=True)

        # Move the staff user into cohort 2, no change to exhibitions viewed
        self.staff_user.cohort = self.cohort2
        self.staff_user.save()
        self.assert_can_view(self.exhibition_no_cohort, can_edit=True)
        self.assert_can_view(self.exhibition_cohort1, can_edit=True)
        self.assert_can_view(self.exhibition_cohort2, can_edit=True)

    def test_view_super(self):

        # Staff can see all exhibitions
        self.performLogin(user='staff')
        self.assert_can_view(self.exhibition_no_cohort, can_edit=True)
        self.assert_can_view(self.exhibition_cohort1, can_edit=True)
        self.assert_can_view(self.exhibition_cohort2, can_edit=True)

        # Move the superuser into cohort 1, no change to exhibitions viewed
        self.super_user.cohort = self.cohort1
        self.super_user.save()
        self.assert_can_view(self.exhibition_no_cohort, can_edit=True)
        self.assert_can_view(self.exhibition_cohort1, can_edit=True)
        self.assert_can_view(self.exhibition_cohort2, can_edit=True)

        # Move the superuser into cohort 2, no change to exhibitions viewed
        self.super_user.cohort = self.cohort2
        self.super_user.save()
        self.assert_can_view(self.exhibition_no_cohort, can_edit=True)
        self.assert_can_view(self.exhibition_cohort1, can_edit=True)
        self.assert_can_view(self.exhibition_cohort2, can_edit=True)


class ExhibitionViewShareLinkIntegrationTests(SeleniumTestCase):

    def test_view_released(self):

        exhibition = Exhibition.objects.create(title='New Exhibition', description='goes here', author=self.user)

        self.selenium.get('%s%s' % (self.live_server_url, reverse('exhibition-view', kwargs={'pk': exhibition.id})))
        self.assertEqual(
            len(self.selenium.find_elements_by_id('exhibition-view-content')),
            1
        )

    def test_view_unreleased(self):
        # Public cannot see unreleased exhibition
        now = timezone.now()
        exhibition = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            released_at = now + timedelta(hours=24),
            author=self.user)

        view_url = '%s%s' % (self.live_server_url, reverse('exhibition-view', kwargs={'pk': exhibition.id}))
        self.selenium.get(view_url)
        self.assertRegexpMatches(self.selenium.page_source, r'403 Forbidden')

        # Staff can, but no share link is shown
        self.performLogin(user='staff')
        self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('exhibition-view-content')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.share-link')),
            0
        )

        # Logout, and release the exhibition to see the share link
        self.performLogout()
        exhibition.released_at = now
        exhibition.save()
        self.selenium.get(view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('exhibition-view-content')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.share-link')),
            1
        )

        # Ensure that visiting the share_link redirects back to this view_url
        share_link = self.selenium.find_element_by_css_selector('.share-link').text
        self.selenium.get(share_link)
        self.assertEqual(self.selenium.current_url, view_url)
        self.assertEqual(
            len(self.selenium.find_elements_by_id('exhibition-view-content')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.share-link')),
            1
        )

        # Move the release date back, logout, and ensure we can't see the exhibition anymore
        exhibition.released_at = now + timedelta(hours=24)
        exhibition.save()
        self.selenium.get(share_link)
        self.assertEqual(self.selenium.current_url, view_url)
        self.assertRegexpMatches(self.selenium.page_source, r'403 Forbidden')


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


class ExhibitionCreateCohortIntegrationTests(CohortMixin, SeleniumTestCase):

    def test_staff_add_exhibition_form(self):

        add_path = reverse('exhibition-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form
        self.assertLogin(add_path, user='staff')

        # login form redirects to add form
        self.assertEquals(
            len(self.selenium.find_elements_by_css_selector('#id_title')),
            1
        )
        self.assertEquals(
            len(self.selenium.find_elements_by_css_selector('#id_description')),
            1
        )
        # Ensure all cohort options are available in the form
        cohort_element = self.selenium.find_element_by_id('id_cohort')
        cohort_options = cohort_element.find_elements_by_tag_name('option')
        self.assertEquals(len(cohort_options), 3)
        self.assertEquals(cohort_options[0].text, "Shared by all cohorts")
        self.assertEquals(cohort_options[1].text, '%s' % self.cohort1)
        self.assertEquals(cohort_options[2].text, '%s' % self.cohort2)

        self.assertEquals(
            len(self.selenium.find_elements_by_css_selector('#save_exhibition')),
            1
        )

    def test_staff_add_exhibition_no_cohort(self):

        add_path = reverse('exhibition-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form
        self.assertLogin(add_path, user='staff')

        # login form redirects to add form
        self.selenium.find_element_by_id('id_title').send_keys('test submission')
        self.selenium.find_element_by_id('id_description').send_keys('description goes here')
        
        # Select "no cohort"
        cohort_element = self.selenium.find_element_by_id('id_cohort')
        cohort_options = cohort_element.find_elements_by_tag_name('option')
        cohort_options[0].click()

        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_exhibition').click()

        # add action redirects to view url
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )

        # ensure that "no cohort" was saved
        match = re.search('(\d+)/$', self.selenium.current_url)
        exhibition = Exhibition.objects.get(pk=match.group(1))
        self.assertEquals(exhibition.cohort, None)

    def test_staff_add_exhibition_default_cohort(self):

        add_path = reverse('exhibition-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form
        self.assertLogin(add_path, user='staff')

        # login form redirects to add form
        self.selenium.find_element_by_id('id_title').send_keys('test submission')
        self.selenium.find_element_by_id('id_description').send_keys('description goes here')
        
        # Click nothing: default cohort is be pre-selected
        cohort_element = self.selenium.find_element_by_id('id_cohort')
        cohort_options = cohort_element.find_elements_by_tag_name('option')
        self.assertTrue(cohort_options[1].is_selected())

        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_exhibition').click()

        # add action redirects to view url
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )

        # ensure that "cohort1" was saved
        match = re.search('(\d+)/$', self.selenium.current_url)
        exhibition = Exhibition.objects.get(pk=match.group(1))
        self.assertEquals(exhibition.cohort, self.cohort1)

    def test_staff_add_exhibition_other_cohort(self):

        add_path = reverse('exhibition-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form
        self.assertLogin(add_path, user='staff')

        # login form redirects to add form
        self.selenium.find_element_by_id('id_title').send_keys('test submission')
        self.selenium.find_element_by_id('id_description').send_keys('description goes here')
        
        # Select "cohort2"
        cohort_element = self.selenium.find_element_by_id('id_cohort')
        cohort_options = cohort_element.find_elements_by_tag_name('option')
        cohort_options[2].click()

        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_exhibition').click()

        # add action redirects to view url
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )

        # ensure that "cohort2" was saved
        match = re.search('(\d+)/$', self.selenium.current_url)
        exhibition = Exhibition.objects.get(pk=match.group(1))
        self.assertEquals(exhibition.cohort, self.cohort2)

    def test_super_add_exhibition_no_cohort(self):

        add_path = reverse('exhibition-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form
        self.assertLogin(add_path, user='super')

        # login form redirects to add form
        self.selenium.find_element_by_id('id_title').send_keys('test submission')
        self.selenium.find_element_by_id('id_description').send_keys('description goes here')
        
        # Select "no cohort"
        cohort_element = self.selenium.find_element_by_id('id_cohort')
        cohort_options = cohort_element.find_elements_by_tag_name('option')
        cohort_options[0].click()

        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_exhibition').click()

        # add action redirects to view url
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )

        # ensure that "no cohort" was saved
        match = re.search('(\d+)/$', self.selenium.current_url)
        exhibition = Exhibition.objects.get(pk=match.group(1))
        self.assertEquals(exhibition.cohort, None)

    def test_super_add_exhibition_default_cohort(self):

        add_path = reverse('exhibition-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form
        self.assertLogin(add_path, user='super')

        # login form redirects to add form
        self.selenium.find_element_by_id('id_title').send_keys('test submission')
        self.selenium.find_element_by_id('id_description').send_keys('description goes here')
        
        # Click nothing: default cohort is be pre-selected
        cohort_element = self.selenium.find_element_by_id('id_cohort')
        cohort_options = cohort_element.find_elements_by_tag_name('option')
        self.assertTrue(cohort_options[1].is_selected())

        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_exhibition').click()

        # add action redirects to view url
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )

        # ensure that "cohort1" was saved
        match = re.search('(\d+)/$', self.selenium.current_url)
        exhibition = Exhibition.objects.get(pk=match.group(1))
        self.assertEquals(exhibition.cohort, self.cohort1)

    def test_super_add_exhibition_other_cohort(self):

        add_path = reverse('exhibition-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form
        self.assertLogin(add_path, user='super')

        # login form redirects to add form
        self.selenium.find_element_by_id('id_title').send_keys('test submission')
        self.selenium.find_element_by_id('id_description').send_keys('description goes here')
        
        # Select "cohort2"
        cohort_element = self.selenium.find_element_by_id('id_cohort')
        cohort_options = cohort_element.find_elements_by_tag_name('option')
        cohort_options[2].click()

        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_exhibition').click()

        # add action redirects to view url
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )

        # ensure that "cohort2" was saved
        match = re.search('(\d+)/$', self.selenium.current_url)
        exhibition = Exhibition.objects.get(pk=match.group(1))
        self.assertEquals(exhibition.cohort, self.cohort2)

    def test_students_cannot_add_exhibition(self):

        add_path = reverse('exhibition-add')
        self.selenium.get('%s%s' % (self.live_server_url, add_path))

        # add redirects to login form, which redirects to list page
        list_path = reverse('exhibition-list')
        self.assertLoginRedirects(add_path, redirect_path=list_path)


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


class ExhibitionImageIntegrationTests(SeleniumTestCase):

    def test_edit_exhibition_image(self):

        exhibition = Exhibition.objects.create(title='Title bar', description='description goes here', author=self.staff_user)

        # exhibition doesn't contain an image yet
        view_path = reverse('exhibition-view', kwargs={'pk': exhibition.id})
        self.selenium.get('%s%s' % (self.live_server_url, view_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition-image')),
            0
        )
        
        # edit redirects to login form
        edit_path = reverse('exhibition-edit', kwargs={'pk': exhibition.id})
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))
        self.assertLogin(edit_path, user='staff')

        # send image file url to form
        image_path = os.path.join(os.getcwd(), 'exhibitions', 'tests', 'img', 'tiny.gif')
        self.selenium.find_element_by_id('id_image').send_keys(image_path)

        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_exhibition').click()

        # add action redirects to view url
        view_path = reverse('exhibition-view', kwargs={'pk': exhibition.id})
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, view_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition-image')),
            1
        )

        # image should be shown in list view too
        list_path = reverse('exhibition-list')
        self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition-image')),
            1
        )

    def test_delete_exhibition_image(self):

        exhibition = Exhibition.objects.create(title='Title bar', description='description goes here', author=self.staff_user)
        # edit redirects to login form
        edit_path = reverse('exhibition-edit', kwargs={'pk': exhibition.id})
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))
        self.assertLogin(edit_path, user='staff')

        # send image file url to form
        image_path = os.path.join(os.getcwd(), 'exhibitions', 'tests', 'img', 'tiny.gif')
        self.selenium.find_element_by_id('id_image').send_keys(image_path)

        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_exhibition').click()

        # add action redirects to view url
        view_path = reverse('exhibition-view', kwargs={'pk': exhibition.id})
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, view_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition-image')),
            1
        )

        # visit the edit form to delete the image
        self.selenium.get('%s%s' % (self.live_server_url, edit_path))

        # click the 'clear' checkbox to remove the image
        self.selenium.find_element_by_id('image-clear_id').click()

        with wait_for_page_load(self.selenium):
            self.selenium.find_element_by_id('save_exhibition').click()

        # add action redirects to view url
        view_path = reverse('exhibition-view', kwargs={'pk': exhibition.id})
        self.assertEqual(self.selenium.current_url, '%s%s' % (self.live_server_url, view_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition-image')),
            0
        )

        # image should be removed from list view too
        list_path = reverse('exhibition-list')
        self.selenium.get('%s%s' % (self.live_server_url, list_path))
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition')),
            1
        )
        self.assertEqual(
            len(self.selenium.find_elements_by_css_selector('.exhibition-image')),
            0
        )
