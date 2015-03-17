from django.test import TestCase
from django.db import IntegrityError
from django.core.urlresolvers import reverse

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

    def test_can_see_private(self):
        student = Artwork(
            author=self.user,
            title='Empty code',
            code='// code goes here')
        self.assertTrue(student.can_see(self.user))
        self.assertFalse(student.can_see(self.staff_user))
        self.assertFalse(student.can_see(self.super_user))

        staff = Artwork(
            author=self.staff_user,
            title='Empty code',
            code='// code goes here')
        self.assertFalse(staff.can_see(self.user))
        self.assertTrue(staff.can_see(self.staff_user))
        self.assertFalse(staff.can_see(self.super_user))

        superuser = Artwork(
            author=self.super_user,
            title='Empty code',
            code='// code goes here')
        self.assertFalse(superuser.can_see(self.user))
        self.assertFalse(superuser.can_see(self.staff_user))
        self.assertTrue(superuser.can_see(self.super_user))

    def test_can_see_shared(self):
        student = Artwork(
            author=self.user,
            title='Empty code',
            shared=1,
            code='// code goes here')
        self.assertTrue(student.can_see(self.user))
        self.assertTrue(student.can_see(self.staff_user))
        self.assertTrue(student.can_see(self.super_user))

        staff = Artwork(
            author=self.staff_user,
            title='Empty code',
            shared=1,
            code='// code goes here')
        self.assertTrue(staff.can_see(self.user))
        self.assertTrue(staff.can_see(self.staff_user))
        self.assertTrue(staff.can_see(self.super_user))

        superuser = Artwork(
            author=self.super_user,
            title='Empty code',
            shared=1,
            code='// code goes here')
        self.assertTrue(superuser.can_see(self.user))
        self.assertTrue(superuser.can_see(self.staff_user))
        self.assertTrue(superuser.can_see(self.super_user))

    def test_can_save_private(self):
        student = Artwork(
            author=self.user,
            title='Empty code',
            code='// code goes here')
        self.assertTrue(student.can_save(self.user))
        self.assertFalse(student.can_save(self.staff_user))
        self.assertFalse(student.can_save(self.super_user))

        staff = Artwork(
            author=self.staff_user,
            title='Empty code',
            code='// code goes here')
        self.assertFalse(staff.can_save(self.user))
        self.assertTrue(staff.can_save(self.staff_user))
        self.assertFalse(staff.can_save(self.super_user))

        superuser = Artwork(
            author=self.super_user,
            title='Empty code',
            code='// code goes here')
        self.assertFalse(superuser.can_save(self.user))
        self.assertFalse(superuser.can_save(self.staff_user))
        self.assertTrue(superuser.can_save(self.super_user))

    def test_cant_save_shared(self):
        student = Artwork(
            author=self.user,
            title='Empty code',
            shared=1,
            code='// code goes here')
        self.assertFalse(student.can_save(self.user))
        self.assertFalse(student.can_save(self.staff_user))
        self.assertFalse(student.can_save(self.super_user))

        staff = Artwork(
            author=self.staff_user,
            title='Empty code',
            shared=1,
            code='// code goes here')
        self.assertFalse(staff.can_save(self.user))
        self.assertFalse(staff.can_save(self.staff_user))
        self.assertFalse(staff.can_save(self.super_user))

        superuser = Artwork(
            author=self.super_user,
            title='Empty code',
            shared=1,
            code='// code goes here')
        self.assertFalse(superuser.can_save(self.user))
        self.assertFalse(superuser.can_save(self.staff_user))
        self.assertFalse(superuser.can_save(self.super_user))

    def test_can_see_private_queryset(self):
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

        public_qs = Artwork.can_see_queryset()
        self.assertEqual(len(public_qs.all()), 0)

        student_qs = Artwork.can_see_queryset(user=self.user)
        self.assertEqual(len(student_qs.all()), 1)
        self.assertEqual(student_qs.all()[0].id, student.id)

        staff_qs = Artwork.can_see_queryset(user=self.staff_user)
        self.assertEqual(len(staff_qs.all()), 1)
        self.assertEqual(staff_qs.all()[0].id, staff.id)

        super_qs = Artwork.can_see_queryset(user=self.super_user)
        self.assertEqual(len(super_qs.all()), 1)
        self.assertEqual(super_qs.all()[0].id, superuser.id)

    def test_can_see_shared_queryset(self):
        student = Artwork(
            author=self.user,
            title='Empty code',
            shared=1,
            code='// code goes here')
        student.save()

        staff = Artwork(
            author=self.staff_user,
            title='Empty code',
            shared=1,
            code='// code goes here')
        staff.save()

        superuser = Artwork(
            author=self.super_user,
            title='Empty code',
            shared=1,
            code='// code goes here')
        superuser.save()

        public_qs = Artwork.can_see_queryset()
        self.assertEqual(len(public_qs.all()), 3)

        student_qs = Artwork.can_see_queryset(user=self.user)
        self.assertEqual(len(student_qs.all()), 3)
        self.assertEqual(student_qs.all()[0].id, student.id)
        self.assertEqual(student_qs.all()[1].id, staff.id)
        self.assertEqual(student_qs.all()[2].id, superuser.id)

        staff_qs = Artwork.can_see_queryset(user=self.staff_user)
        self.assertEqual(len(staff_qs.all()), 3)
        self.assertEqual(student_qs.all()[0].id, student.id)
        self.assertEqual(student_qs.all()[1].id, staff.id)
        self.assertEqual(student_qs.all()[2].id, superuser.id)

        super_qs = Artwork.can_see_queryset(user=self.super_user)
        self.assertEqual(len(super_qs.all()), 3)
        self.assertEqual(student_qs.all()[0].id, student.id)
        self.assertEqual(student_qs.all()[1].id, staff.id)
        self.assertEqual(student_qs.all()[2].id, superuser.id)

    def test_can_save_private_queryset(self):
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

        public_qs = Artwork.can_save_queryset()
        self.assertEqual(len(public_qs.all()), 0)

        student_qs = Artwork.can_save_queryset(user=self.user)
        self.assertEqual(len(student_qs.all()), 1)
        self.assertEqual(student_qs.all()[0].id, student.id)

        staff_qs = Artwork.can_save_queryset(user=self.staff_user)
        self.assertEqual(len(staff_qs.all()), 1)
        self.assertEqual(staff_qs.all()[0].id, staff.id)

        super_qs = Artwork.can_save_queryset(user=self.super_user)
        self.assertEqual(len(super_qs.all()), 1)
        self.assertEqual(super_qs.all()[0].id, superuser.id)

    def test_can_save_shared_queryset(self):
        student = Artwork(
            author=self.user,
            title='Empty code',
            shared=1,
            code='// code goes here')
        student.save()

        staff = Artwork(
            author=self.staff_user,
            title='Empty code',
            shared=1,
            code='// code goes here')
        staff.save()

        superuser = Artwork(
            author=self.super_user,
            title='Empty code',
            shared=1,
            code='// code goes here')
        superuser.save()

        public_qs = Artwork.can_save_queryset()
        self.assertEqual(len(public_qs.all()), 0)

        student_qs = Artwork.can_save_queryset(user=self.user)
        self.assertEqual(len(student_qs.all()), 0)

        staff_qs = Artwork.can_save_queryset(user=self.staff_user)
        self.assertEqual(len(staff_qs.all()), 0)

        super_qs = Artwork.can_save_queryset(user=self.super_user)
        self.assertEqual(len(super_qs.all()), 0)

    def test_get_absolute_url_private(self):
        artwork = Artwork.objects.create(title='Empty code', code='// code goes here', author=self.user)
        view_url = reverse('artwork-edit', kwargs={'pk': artwork.id})
        abs_url = artwork.get_absolute_url()
        self.assertEqual(view_url, abs_url)

    def test_get_absolute_url_shared(self):
        artwork = Artwork.objects.create(title='Empty code', code='// code goes here', shared=1, author=self.user)
        shared_url = reverse('submission-view', kwargs={'pk': artwork.shared})
        abs_url = artwork.get_absolute_url()
        self.assertEqual(shared_url, abs_url)


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
