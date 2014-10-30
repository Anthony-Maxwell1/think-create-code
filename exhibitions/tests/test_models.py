from django.test import TestCase
from django.db import IntegrityError
from django.utils import timezone
from datetime import datetime, timedelta

from gallery.tests import UserSetUp
from exhibitions.models import Exhibition, ExhibitionForm


class ExhibitionTests(UserSetUp, TestCase):
    """Exhibition model tests."""

    def test_str(self):
        
        exhibition = Exhibition(title='New Exhibition', description='description goes here')

        self.assertEquals(
            str(exhibition),
            'New Exhibition'
        )

    def test_released_yet(self):
        now = timezone.now()

        # Released yesterday
        yesterday = Exhibition(
            title='New Exhibition',
            description='description goes here', 
            released_at=now + timedelta(hours=-24))
        self.assertTrue(yesterday.released_yet)

        # Released today
        today = Exhibition(
            title='New Exhibition',
            description='description goes here',
            released_at=now)
        self.assertTrue(today.released_yet)

        # Released tomorrow
        tomorrow = Exhibition(
            title='New Exhibition',
            description='description goes here',
            released_at=now + timedelta(hours=24))
        self.assertFalse(tomorrow.released_yet)

    def test_can_see(self):
        now = timezone.now()

        # Released yesterday
        yesterday = Exhibition(
            title='New Exhibition',
            description='description goes here', 
            released_at=now + timedelta(hours=-24))
        self.assertTrue(yesterday.can_see(self.user))
        self.assertTrue(yesterday.can_see(self.staff_user))
        self.assertTrue(yesterday.can_see(self.super_user))

        # Released today
        today = Exhibition(
            title='New Exhibition',
            description='description goes here',
            released_at=now)
        self.assertTrue(today.can_see(self.user))
        self.assertTrue(today.can_see(self.staff_user))
        self.assertTrue(today.can_see(self.super_user))

        # Released today
        tomorrow = Exhibition(
            title='New Exhibition',
            description='description goes here',
            released_at=now + timedelta(hours=24))
        self.assertFalse(tomorrow.can_see(self.user))
        self.assertTrue(tomorrow.can_see(self.staff_user))
        self.assertTrue(tomorrow.can_see(self.super_user))

    def test_can_save(self):
        exhibition = Exhibition(
            author=self.super_user,
            title='New Exhibition',
            description='description goes here',
            released_at=timezone.now())
        self.assertFalse(exhibition.can_save(self.user))
        self.assertTrue(exhibition.can_save(self.staff_user))
        self.assertTrue(exhibition.can_save(self.super_user))

    def test_can_see_queryset(self):
        now = timezone.now()

        # Released yesterday
        yesterday = Exhibition(
            author=self.user,
            title='Yesterday Exhibition',
            description='description goes here', 
            released_at=now + timedelta(hours=-24))
        yesterday.save()

        # Released today
        today = Exhibition(
            author=self.user,
            title='Today Exhibition',
            description='description goes here',
            released_at=now)
        today.save()

        # Released tomorrow
        tomorrow = Exhibition(
            author=self.user,
            title='Tomorrow Exhibition',
            description='description goes here',
            released_at=now + timedelta(hours=24))
        tomorrow.save()

        student_qs = Exhibition.can_see_queryset(Exhibition.objects, self.user)
        self.assertEqual(len(student_qs.all()), 2)
        self.assertEqual(student_qs.all()[0].id, yesterday.id)
        self.assertEqual(student_qs.all()[1].id, today.id)

        staff_qs = Exhibition.can_see_queryset(Exhibition.objects, self.staff_user)
        self.assertEqual(len(staff_qs.all()), 3)
        self.assertEqual(staff_qs.all()[0].id, yesterday.id)
        self.assertEqual(staff_qs.all()[1].id, today.id)
        self.assertEqual(staff_qs.all()[2].id, tomorrow.id)

        super_qs = Exhibition.can_see_queryset(Exhibition.objects, self.super_user)
        self.assertEqual(len(super_qs.all()), 3)
        self.assertEqual(super_qs.all()[0].id, yesterday.id)
        self.assertEqual(super_qs.all()[1].id, today.id)
        self.assertEqual(super_qs.all()[2].id, tomorrow.id)


class ExhibitionModelFormTests(UserSetUp, TestCase):
    """model.ExhibitionForm tests."""

    def test_login(self):
        form_data = {
            'title': 'New exhibition',
            'description': 'description goes here',
            'released_at': timezone.now(),
        }

        # Form requires logged-in user
        form = ExhibitionForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertRaises(IntegrityError, form.save)

    def test_validation(self):

        form_data = {
            'title': 'New exhibition',
            'description': 'description goes here',
            'released_at': timezone.now(),
        }

        form = ExhibitionForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.instance.title, form_data['title'])
        self.assertEqual(form.instance.description, form_data['description'])

        # Have to set the author before we can save
        form.instance.author_id = self.user.id
        form.save()

        self.assertEqual(
            Exhibition.objects.get(id=form.instance.id).title,
            'New exhibition'
        )

    def test_valid_release_date(self):

        released_at = datetime(2010, 1, 1, 1, 1, 0, 0, timezone.get_default_timezone())
        form_data = {
            'title': 'New exhibition',
            'description': 'description goes here',
            'released_at': released_at,
        }

        form = ExhibitionForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.instance.title, form_data['title'])
        self.assertEqual(form.instance.description, form_data['description'])
        self.assertEqual(form.instance.released_at, form_data['released_at'])

        # Have to set the author before we can save
        form.instance.author_id = self.user.id
        form.save()

        self.assertEqual(
            Exhibition.objects.get(id=form.instance.id).released_at,
            released_at
        )

    def test_invalid_release_date(self):

        released_at = 4

        form_data = {
            'title': 'New exhibition',
            'description': 'description goes here',
            'released_at': released_at,
        }

        form = ExhibitionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.instance.title, form_data['title'])
        self.assertEqual(form.instance.description, form_data['description'])

        form.instance.author_id = self.user.id

        # Invalid released_at gives value error
        self.assertRaises(ValueError, form.save)

    def test_invalidation(self):
        form_data = {
            'title': 'New exhibition',
        }

        form = ExhibitionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.instance.title, form_data['title'])

        self.assertRaises(ValueError, form.save)
