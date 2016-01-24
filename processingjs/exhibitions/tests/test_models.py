from django.test import TestCase
from django.db import IntegrityError
from django.utils import timezone
from datetime import datetime, timedelta
from django.core import files
from django.contrib.auth import get_user_model

from django_adelaidex.util.test import UserSetUp
from django_adelaidex.lti.models import Cohort
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


class ExhibitionNoCohortTests(UserSetUp, TestCase):
    """Exhibition model tests, with no cohorts."""

    def setUp(self):
        super(ExhibitionNoCohortTests, self).setUp()
        self.no_cohort_user = get_user_model().objects.create(username='no_cohort')
        self.no_cohort_user.cohort = None
        self.cohort1_user = get_user_model().objects.create(username='cohort1')
        self.cohort2_user = get_user_model().objects.create(username='cohort2')

    def test_can_see(self):
        # All users can see exhibitions with null cohorts
        exhibition_all = Exhibition(
            title='New Exhibition',
            description='description goes here', 
        )
        self.assertTrue(exhibition_all.can_see(self.no_cohort_user))
        self.assertTrue(exhibition_all.can_see(self.cohort1_user))
        self.assertTrue(exhibition_all.can_see(self.cohort2_user))

        self.no_cohort_user.is_staff = True
        self.cohort1_user.is_staff = True
        self.cohort2_user.is_staff = True
        self.assertTrue(exhibition_all.can_see(self.no_cohort_user))
        self.assertTrue(exhibition_all.can_see(self.cohort1_user))
        self.assertTrue(exhibition_all.can_see(self.cohort2_user))

        self.no_cohort_user.is_staff = False
        self.cohort1_user.is_staff = False
        self.cohort2_user.is_staff = False
        self.no_cohort_user.is_superuser = True
        self.cohort1_user.is_superuser = True
        self.cohort2_user.is_superuser = True
        self.assertTrue(exhibition_all.can_see(self.no_cohort_user))
        self.assertTrue(exhibition_all.can_see(self.cohort1_user))
        self.assertTrue(exhibition_all.can_see(self.cohort2_user))

    def test_can_save(self):
        # Staff & super users can save all exhibitions
        exhibition_all = Exhibition(
            title='New Exhibition',
            description='description goes here', 
        )
        self.assertFalse(exhibition_all.can_save(self.no_cohort_user))
        self.assertFalse(exhibition_all.can_save(self.cohort1_user))
        self.assertFalse(exhibition_all.can_save(self.cohort2_user))

        self.no_cohort_user.is_staff = True
        self.cohort1_user.is_staff = True
        self.cohort2_user.is_staff = True
        self.assertTrue(exhibition_all.can_save(self.no_cohort_user))
        self.assertTrue(exhibition_all.can_save(self.cohort1_user))
        self.assertTrue(exhibition_all.can_save(self.cohort2_user))

        self.no_cohort_user.is_staff = False
        self.cohort1_user.is_staff = False
        self.cohort2_user.is_staff = False
        self.no_cohort_user.is_superuser = True
        self.cohort1_user.is_superuser = True
        self.cohort2_user.is_superuser = True
        self.assertTrue(exhibition_all.can_save(self.no_cohort_user))
        self.assertTrue(exhibition_all.can_save(self.cohort1_user))
        self.assertTrue(exhibition_all.can_save(self.cohort2_user))

    def test_can_see_queryset(self):
        exhibition_all = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            author=self.staff_user,
            cohort=None,
        )
        # All students can see the no-cohort exhibition
        no_cohort_user_qs = Exhibition.can_see_queryset(user=self.no_cohort_user)
        self.assertEqual(no_cohort_user_qs.count(), 1)
        self.assertEqual(no_cohort_user_qs.all()[0], exhibition_all)

        cohort1_user_qs = Exhibition.can_see_queryset(user=self.cohort1_user)
        self.assertEqual(cohort1_user_qs.count(), 1)
        self.assertEqual(cohort1_user_qs.all()[0], exhibition_all)

        cohort2_user_qs = Exhibition.can_see_queryset(user=self.cohort2_user)
        self.assertEqual(cohort2_user_qs.count(), 1)
        self.assertEqual(cohort2_user_qs.all()[0], exhibition_all)

        # Staff access doesn't change cohort queryset (even though staff can
        # see all exhibitions)
        self.no_cohort_user.is_staff = True
        no_cohort_user_qs = Exhibition.can_see_queryset(user=self.no_cohort_user)
        self.assertEqual(no_cohort_user_qs.count(), 1)
        self.assertEqual(no_cohort_user_qs.all()[0], exhibition_all)

        self.cohort1_user.is_staff = True
        cohort1_user_qs = Exhibition.can_see_queryset(user=self.cohort1_user)
        self.assertEqual(cohort1_user_qs.count(), 1)
        self.assertEqual(cohort1_user_qs.all()[0], exhibition_all)

        self.cohort2_user.is_staff = True
        cohort2_user_qs = Exhibition.can_see_queryset(user=self.cohort2_user)
        self.assertEqual(cohort2_user_qs.count(), 1)
        self.assertEqual(cohort2_user_qs.all()[0], exhibition_all)

        # And neither does superuser access
        self.no_cohort_user.is_staff = False
        self.no_cohort_user.is_superuser = True
        no_cohort_user_qs = Exhibition.can_see_queryset(user=self.no_cohort_user)
        self.assertEqual(no_cohort_user_qs.count(), 1)
        self.assertEqual(no_cohort_user_qs.all()[0], exhibition_all)

        self.cohort1_user.is_staff = False
        self.cohort1_user.is_superuser = True
        cohort1_user_qs = Exhibition.can_see_queryset(user=self.cohort1_user)
        self.assertEqual(cohort1_user_qs.count(), 1)
        self.assertEqual(cohort1_user_qs.all()[0], exhibition_all)

        self.cohort2_user.is_staff = False
        self.cohort2_user.is_superuser = True
        cohort2_user_qs = Exhibition.can_see_queryset(user=self.cohort2_user)
        self.assertEqual(cohort2_user_qs.count(), 1)
        self.assertEqual(cohort2_user_qs.all()[0], exhibition_all)


class ExhibitionCohortTests(UserSetUp, TestCase):

    def setUp(self):
        super(ExhibitionCohortTests, self).setUp()
        self.no_cohort_user = get_user_model().objects.create(username='no_cohort')
        self.no_cohort_user.cohort = None
        self.no_cohort_user.save()

        self.cohort1_user = get_user_model().objects.create(username='cohort1')
        self.cohort2_user = get_user_model().objects.create(username='cohort2')

        self.cohort1 = Cohort.objects.create(
            title='Cohort 1',
            oauth_key='abc',
            oauth_secret='abc',
            is_default=True,
        )
        self.cohort1_user.cohort = self.cohort1
        self.cohort1_user.save()

        self.cohort2 = Cohort.objects.create(
            title='Cohort 2',
            oauth_key='def',
            oauth_secret='def',
        )
        self.cohort2_user.cohort = self.cohort2
        self.cohort2_user.save()

    def test_can_see_null_cohorts(self):

        # All users can see exhibitions with null cohorts
        exhibition_all = Exhibition(
            title='New Exhibition',
            description='description goes here', 
        )
        self.assertTrue(exhibition_all.can_see(self.no_cohort_user))
        self.assertTrue(exhibition_all.can_see(self.cohort1_user))
        self.assertTrue(exhibition_all.can_see(self.cohort2_user))

        self.no_cohort_user.is_staff = True
        self.cohort1_user.is_staff = True
        self.cohort2_user.is_staff = True
        self.assertTrue(exhibition_all.can_see(self.no_cohort_user))
        self.assertTrue(exhibition_all.can_see(self.cohort1_user))
        self.assertTrue(exhibition_all.can_see(self.cohort2_user))

        self.no_cohort_user.is_staff = False
        self.cohort1_user.is_staff = False
        self.cohort2_user.is_staff = False
        self.no_cohort_user.is_superuser = True
        self.cohort1_user.is_superuser = True
        self.cohort2_user.is_superuser = True
        self.assertTrue(exhibition_all.can_see(self.no_cohort_user))
        self.assertTrue(exhibition_all.can_see(self.cohort1_user))
        self.assertTrue(exhibition_all.can_see(self.cohort2_user))

    def test_can_see_default_cohort(self):

        # Only students in cohort1 (or with no cohort, i.e. the default cohort)
        # can see exhibitions for the default cohort1
        exhibition_cohort1 = Exhibition(
            title='New Exhibition',
            description='description goes here',
            cohort=self.cohort1)
        self.assertTrue(exhibition_cohort1.can_see(self.no_cohort_user))
        self.assertTrue(exhibition_cohort1.can_see(self.cohort1_user))
        self.assertFalse(exhibition_cohort1.can_see(self.cohort2_user))

        # Staff can see all exhibitions
        self.no_cohort_user.is_staff = True
        self.cohort1_user.is_staff = True
        self.cohort2_user.is_staff = True
        self.assertTrue(exhibition_cohort1.can_see(self.no_cohort_user))
        self.assertTrue(exhibition_cohort1.can_see(self.cohort1_user))
        self.assertTrue(exhibition_cohort1.can_see(self.cohort2_user))

        # Super users can see all exhibitions 
        self.no_cohort_user.is_staff = False
        self.cohort1_user.is_staff = False
        self.cohort2_user.is_staff = False
        self.no_cohort_user.is_superuser = True
        self.cohort1_user.is_superuser = True
        self.cohort2_user.is_superuser = True
        self.assertTrue(exhibition_cohort1.can_see(self.no_cohort_user))
        self.assertTrue(exhibition_cohort1.can_see(self.cohort1_user))
        self.assertTrue(exhibition_cohort1.can_see(self.cohort2_user))

    def test_can_see_non_default_cohort(self):

        # Only users in cohort2 can see exhibitions for cohort2
        exhibition_cohort2 = Exhibition(
            title='New Exhibition',
            description='description goes here',
            cohort=self.cohort2)
        self.assertFalse(exhibition_cohort2.can_see(self.no_cohort_user))
        self.assertFalse(exhibition_cohort2.can_see(self.cohort1_user))
        self.assertTrue(exhibition_cohort2.can_see(self.cohort2_user))

        # Staff can see all exhibitions
        self.no_cohort_user.is_staff = True
        self.cohort1_user.is_staff = True
        self.cohort2_user.is_staff = True
        self.assertTrue(exhibition_cohort2.can_see(self.no_cohort_user))
        self.assertTrue(exhibition_cohort2.can_see(self.cohort1_user))
        self.assertTrue(exhibition_cohort2.can_see(self.cohort2_user))

        # Super users can see all exhibitions 
        self.no_cohort_user.is_staff = False
        self.cohort1_user.is_staff = False
        self.cohort2_user.is_staff = False
        self.no_cohort_user.is_superuser = True
        self.cohort1_user.is_superuser = True
        self.cohort2_user.is_superuser = True
        self.assertTrue(exhibition_cohort2.can_see(self.no_cohort_user))
        self.assertTrue(exhibition_cohort2.can_see(self.cohort1_user))
        self.assertTrue(exhibition_cohort2.can_see(self.cohort2_user))

    def test_can_save_null_cohort(self):

        # Students cannot save exhibitions
        exhibition_all = Exhibition(
            title='New Exhibition',
            description='description goes here', 
        )
        self.assertFalse(exhibition_all.can_save(self.no_cohort_user))
        self.assertFalse(exhibition_all.can_save(self.cohort1_user))
        self.assertFalse(exhibition_all.can_save(self.cohort2_user))

        # Staff users can save all exhibitions
        self.no_cohort_user.is_staff = True
        self.cohort1_user.is_staff = True
        self.cohort2_user.is_staff = True
        self.assertTrue(exhibition_all.can_save(self.no_cohort_user))
        self.assertTrue(exhibition_all.can_save(self.cohort1_user))
        self.assertTrue(exhibition_all.can_save(self.cohort2_user))

        # Super users can save exhibitions
        self.no_cohort_user.is_staff = False
        self.cohort1_user.is_staff = False
        self.cohort2_user.is_staff = False
        self.no_cohort_user.is_superuser = True
        self.cohort1_user.is_superuser = True
        self.cohort2_user.is_superuser = True
        self.assertTrue(exhibition_all.can_save(self.no_cohort_user))
        self.assertTrue(exhibition_all.can_save(self.cohort1_user))
        self.assertTrue(exhibition_all.can_save(self.cohort2_user))

    def test_can_save_default_cohort(self):

        # Students cannot save exhibitions
        exhibition_cohort1 = Exhibition(
            title='New Exhibition',
            description='description goes here',
            cohort=self.cohort1)
        self.assertFalse(exhibition_cohort1.can_save(self.no_cohort_user))
        self.assertFalse(exhibition_cohort1.can_save(self.cohort1_user))
        self.assertFalse(exhibition_cohort1.can_save(self.cohort2_user))

        # Staff members can save all exhibitions
        self.no_cohort_user.is_staff = True
        self.cohort1_user.is_staff = True
        self.cohort2_user.is_staff = True
        self.assertTrue(exhibition_cohort1.can_save(self.no_cohort_user))
        self.assertTrue(exhibition_cohort1.can_save(self.cohort1_user))
        self.assertTrue(exhibition_cohort1.can_save(self.cohort2_user))

        self.no_cohort_user.is_staff = False
        self.cohort1_user.is_staff = False
        self.cohort2_user.is_staff = False
        self.no_cohort_user.is_superuser = True
        self.cohort1_user.is_superuser = True
        self.cohort2_user.is_superuser = True
        self.assertTrue(exhibition_cohort1.can_save(self.no_cohort_user))
        self.assertTrue(exhibition_cohort1.can_save(self.cohort1_user))
        self.assertTrue(exhibition_cohort1.can_save(self.cohort2_user))

    def test_can_save_non_default_cohort(self):

        # Students cannot save exhibitions
        exhibition_cohort2 = Exhibition(
            title='New Exhibition',
            description='description goes here',
            cohort=self.cohort2)
        self.assertFalse(exhibition_cohort2.can_save(self.no_cohort_user))
        self.assertFalse(exhibition_cohort2.can_save(self.cohort1_user))
        self.assertFalse(exhibition_cohort2.can_save(self.cohort2_user))

        # Staff members can save all exhibitions
        self.no_cohort_user.is_staff = True
        self.cohort1_user.is_staff = True
        self.cohort2_user.is_staff = True
        self.assertTrue(exhibition_cohort2.can_save(self.no_cohort_user))
        self.assertTrue(exhibition_cohort2.can_save(self.cohort1_user))
        self.assertTrue(exhibition_cohort2.can_save(self.cohort2_user))

        self.no_cohort_user.is_staff = False
        self.cohort1_user.is_staff = False
        self.cohort2_user.is_staff = False
        self.no_cohort_user.is_superuser = True
        self.cohort1_user.is_superuser = True
        self.cohort2_user.is_superuser = True
        self.assertTrue(exhibition_cohort2.can_save(self.no_cohort_user))
        self.assertTrue(exhibition_cohort2.can_save(self.cohort1_user))
        self.assertTrue(exhibition_cohort2.can_save(self.cohort2_user))

    def test_can_see_queryset(self):

        exhibition_all = Exhibition.objects.create(
            title='New Exhibition',
            description='description goes here',
            author=self.staff_user,
            cohort=None,
        )
        exhibition_cohort1 = Exhibition.objects.create(
            title='Exhibition 1',
            description='description goes here', 
            author=self.staff_user,
            cohort=self.cohort1,
        )
        exhibition_cohort2 = Exhibition.objects.create(
            title='Exhibition 2',
            description='description goes here', 
            author=self.staff_user,
            cohort=self.cohort2,
        )

        # No cohort student can see the no cohort exhibition, and the default cohort
        no_cohort_user_qs = Exhibition.can_see_queryset(user=self.no_cohort_user)
        self.assertEqual(no_cohort_user_qs.count(), 2)
        self.assertEqual(no_cohort_user_qs.all()[0], exhibition_all)
        self.assertEqual(no_cohort_user_qs.all()[1], exhibition_cohort1)

        # Cohort1 student gets the no cohort + cohort1 exhibitions
        cohort1_user_qs = Exhibition.can_see_queryset(user=self.cohort1_user)
        self.assertEqual(cohort1_user_qs.count(), 2)
        self.assertEqual(cohort1_user_qs.all()[0], exhibition_all)
        self.assertEqual(cohort1_user_qs.all()[1], exhibition_cohort1)

        # Cohort2 student gets the no cohort + cohort2 exhibitions
        cohort2_user_qs = Exhibition.can_see_queryset(user=self.cohort2_user)
        self.assertEqual(cohort2_user_qs.count(), 2)
        self.assertEqual(cohort2_user_qs.all()[0], exhibition_all)
        self.assertEqual(cohort2_user_qs.all()[1], exhibition_cohort2)

        # Staff access doesn't change cohort queryset (even though staff can
        # see all exhibitions)
        self.no_cohort_user.is_staff = True
        no_cohort_user_qs = Exhibition.can_see_queryset(user=self.no_cohort_user)
        self.assertEqual(no_cohort_user_qs.count(), 2)
        self.assertEqual(no_cohort_user_qs.all()[0], exhibition_all)
        self.assertEqual(no_cohort_user_qs.all()[1], exhibition_cohort1)

        self.cohort1_user.is_staff = True
        cohort1_user_qs = Exhibition.can_see_queryset(user=self.cohort1_user)
        self.assertEqual(cohort1_user_qs.count(), 2)
        self.assertEqual(cohort1_user_qs.all()[0], exhibition_all)
        self.assertEqual(cohort1_user_qs.all()[1], exhibition_cohort1)

        self.cohort2_user.is_staff = True
        cohort2_user_qs = Exhibition.can_see_queryset(user=self.cohort2_user)
        self.assertEqual(cohort2_user_qs.count(), 2)
        self.assertEqual(cohort2_user_qs.all()[0], exhibition_all)
        self.assertEqual(cohort2_user_qs.all()[1], exhibition_cohort2)


        # But superusers see all cohorts in the queryset
        self.no_cohort_user.is_staff = False
        self.no_cohort_user.is_superuser = True
        no_cohort_user_qs = Exhibition.can_see_queryset(user=self.no_cohort_user)
        self.assertEqual(no_cohort_user_qs.count(), 3)
        self.assertEqual(no_cohort_user_qs.all()[0], exhibition_all)
        self.assertEqual(no_cohort_user_qs.all()[1], exhibition_cohort1)
        self.assertEqual(no_cohort_user_qs.all()[2], exhibition_cohort2)

        self.cohort1_user.is_staff = False
        self.cohort1_user.is_superuser = True
        cohort1_user_qs = Exhibition.can_see_queryset(user=self.cohort1_user)
        self.assertEqual(cohort1_user_qs.count(), 3)
        self.assertEqual(cohort1_user_qs.all()[0], exhibition_all)
        self.assertEqual(cohort1_user_qs.all()[1], exhibition_cohort1)
        self.assertEqual(cohort1_user_qs.all()[2], exhibition_cohort2)

        self.cohort2_user.is_staff = False
        self.cohort2_user.is_superuser = True
        cohort2_user_qs = Exhibition.can_see_queryset(user=self.cohort2_user)
        self.assertEqual(cohort2_user_qs.count(), 3)
        self.assertEqual(cohort2_user_qs.all()[0], exhibition_all)
        self.assertEqual(cohort2_user_qs.all()[1], exhibition_cohort1)
        self.assertEqual(cohort2_user_qs.all()[2], exhibition_cohort2)


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
