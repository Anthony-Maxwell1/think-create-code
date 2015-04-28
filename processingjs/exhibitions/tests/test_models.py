from django.test import TestCase
from django.db import IntegrityError
from django.utils import timezone
from datetime import datetime, timedelta
from django.core import files

from uofa.test import UserSetUp
from exhibitions.models import Exhibition, ExhibitionForm
from database_files.models import File


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

        # Students cannot save exhibitions
        student = Exhibition(
            author=self.user,
            title='New Exhibition',
            description='description goes here',
            released_at=timezone.now())
        self.assertFalse(student.can_save(self.user))
        self.assertTrue(student.can_save(self.staff_user))
        self.assertTrue(student.can_save(self.super_user))

        staff = Exhibition(
            author=self.staff_user,
            title='New Exhibition',
            description='description goes here',
            released_at=timezone.now())
        self.assertFalse(staff.can_save(self.user))
        self.assertTrue(staff.can_save(self.staff_user))
        self.assertTrue(staff.can_save(self.super_user))

        superuser = Exhibition(
            author=self.super_user,
            title='New Exhibition',
            description='description goes here',
            released_at=timezone.now())
        self.assertFalse(superuser.can_save(self.user))
        self.assertTrue(superuser.can_save(self.staff_user))
        self.assertTrue(superuser.can_save(self.super_user))

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

        public_qs = Exhibition.can_see_queryset(Exhibition.objects)
        self.assertEqual(len(public_qs.all()), 2)
        self.assertEqual(public_qs.all()[0].id, yesterday.id)
        self.assertEqual(public_qs.all()[1].id, today.id)

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


class ExhibitionImageTests(UserSetUp, TestCase):

    PNG_IMAGE = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAGUlEQVQYV2M8c+bMfwYiAOOoQnyhRP3gAQCJgSHpCB6weAAAAABJRU5ErkJggg=='

    @staticmethod
    def create_tmp_file(suffix='.txt', data=''):
        '''Creates a new temp file.
           Default arguments create a 10x10 gray png'''
        tmp_file = files.temp.NamedTemporaryFile(
            suffix=suffix,
            dir=files.temp.gettempdir()
        )
        tmp_file.write(data)
        tmp_file.seek(0)
        return tmp_file

    def test_add_image(self):
        suffix = '.png'
        tmp_file = self.create_tmp_file(suffix=suffix, data=self.PNG_IMAGE)
        exhibition = Exhibition.objects.create(
            author=self.user,
            title='New Exhibition',
            description='description goes here',
            released_at=timezone.now(),
            image=files.File(tmp_file),
        )
        self.assertEqual(File.objects.count(), 1)

        exhibition = Exhibition.objects.get(pk=exhibition.id)
        self.assertEqual(exhibition.image.file.name[-1*len(suffix):], suffix)
        self.assertEqual(exhibition.image.file.read(), self.PNG_IMAGE)
        self.assertEqual(exhibition.image.file.size, len(self.PNG_IMAGE))

    def test_delete_exhibition(self):
        suffix = '.png'
        tmp_file = self.create_tmp_file(suffix=suffix, data=self.PNG_IMAGE)
        exhibition = Exhibition.objects.create(
            author=self.user,
            title='New Exhibition',
            description='description goes here',
            released_at=timezone.now(),
            image=files.File(tmp_file),
        )
        self.assertEqual(File.objects.count(), 1)

        exhibition = Exhibition.objects.get(pk=exhibition.id)
        exhibition.delete()
        self.assertEqual(File.objects.count(), 0)

    def test_remove_image(self):
        suffix = '.png'
        tmp_file = self.create_tmp_file(suffix=suffix, data=self.PNG_IMAGE)
        exhibition = Exhibition.objects.create(
            author=self.user,
            title='New Exhibition',
            description='description goes here',
            released_at=timezone.now(),
            image=files.File(tmp_file),
        )
        self.assertEqual(File.objects.count(), 1)

        exhibition = Exhibition.objects.get(pk=exhibition.id)
        exhibition.image = None
        exhibition.save()
        self.assertEqual(File.objects.count(), 0)

    def test_change_image(self):
        suffix = '.png'
        tmp_file1 = self.create_tmp_file(suffix=suffix, data=self.PNG_IMAGE)
        tmp_file2 = self.create_tmp_file(suffix=suffix, data=self.PNG_IMAGE)
        exhibition = Exhibition.objects.create(
            author=self.user,
            title='New Exhibition',
            description='description goes here',
            released_at=timezone.now(),
            image=files.File(tmp_file1),
        )
        self.assertEqual(File.objects.count(), 1)

        exhibition = Exhibition.objects.get(pk=exhibition.id)
        exhibition.image = files.File(tmp_file2)
        exhibition.save()
        self.assertEqual(File.objects.count(), 1)


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
