from django.test import TestCase
from django.db import IntegrityError

from artwork.models import Artwork, ArtworkForm
from uofa.test import UserSetUp

class ArtworkTests(UserSetUp, TestCase):
    """Artwork model tests."""

    def test_str(self):
        
        artwork = Artwork(title='Empty code', code='// code goes here')

        self.assertEquals(
            str(artwork),
            'Empty code'
        )

    def test_can_save(self):
        student = Artwork(
            author=self.user,
            title='Empty code',
            code='// code goes here')
        self.assertTrue(student.can_save(self.user))
        self.assertTrue(student.can_save(self.staff_user))
        self.assertTrue(student.can_save(self.super_user))

        staff = Artwork(
            author=self.staff_user,
            title='Empty code',
            code='// code goes here')
        self.assertFalse(staff.can_save(self.user))
        self.assertTrue(staff.can_save(self.staff_user))
        self.assertTrue(staff.can_save(self.super_user))

        superuser = Artwork(
            author=self.super_user,
            title='Empty code',
            code='// code goes here')
        self.assertFalse(superuser.can_save(self.user))
        self.assertTrue(superuser.can_save(self.staff_user))
        self.assertTrue(superuser.can_save(self.super_user))

    def test_can_submit_queryset(self):
        student = Artwork(
            author=self.user,
            title='Empty code',
            code='// code goes here')
        student.save()

        staff = Artwork(
            author=self.staff_user,
            title='Empty code',
            code='// code goes here')
        staff.save()

        superuser = Artwork(
            author=self.super_user,
            title='Empty code',
            code='// code goes here')
        superuser.save()

        public_qs = Artwork.can_submit_queryset(Artwork.objects)
        self.assertEqual(len(public_qs.all()), 0)

        student_qs = Artwork.can_submit_queryset(Artwork.objects, self.user)
        self.assertEqual(len(student_qs.all()), 1)
        self.assertEqual(student_qs.all()[0].id, student.id)

        staff_qs = Artwork.can_submit_queryset(Artwork.objects, self.staff_user)
        self.assertEqual(len(staff_qs.all()), 3)
        self.assertEqual(staff_qs.all()[0].id, student.id)
        self.assertEqual(staff_qs.all()[1].id, staff.id)
        self.assertEqual(staff_qs.all()[2].id, superuser.id)

        super_qs = Artwork.can_submit_queryset(Artwork.objects, self.super_user)
        self.assertEqual(len(super_qs.all()), 3)
        self.assertEqual(super_qs.all()[0].id, student.id)
        self.assertEqual(super_qs.all()[1].id, staff.id)
        self.assertEqual(super_qs.all()[2].id, superuser.id)


class ArtworkModelFormTests(UserSetUp, TestCase):
    """model.ArtworkForm tests."""

    def test_login(self):
        form_data = {
            'title': 'Title bar',
            'code': '// code goes here',
        }

        # Form requires logged-in user
        form = ArtworkForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertRaises(IntegrityError, form.save)

    def test_validation(self):

        form_data = {
            'title': 'Title bar',
            'code': '// code goes here'
        }

        form = ArtworkForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.instance.title, form_data['title'])
        self.assertEqual(form.instance.code, form_data['code'])

        # Have to set the author before we can save
        form.instance.author_id = self.user.id
        form.save()

        self.assertEqual(
            Artwork.objects.get(id=form.instance.id).title,
            'Title bar'
        )

    def test_invalidation(self):
        form_data = {
            'title': 'Title bar',
        }

        form = ArtworkForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.instance.title, form_data['title'])

        self.assertRaises(ValueError, form.save)
