from django.test import TestCase
from django.db import IntegrityError
from django.utils import timezone
from datetime import datetime

from exhibitions.models import Exhibition, ExhibitionForm
from gallery.tests import UserSetUp
from artwork.models import Artwork


class ExhibitionTests(TestCase):
    """Exhibition model tests."""

    def test_str(self):
        
        exhibition = Exhibition(title='New Exhibition', description='description goes here')

        self.assertEquals(
            str(exhibition),
            'New Exhibition'
        )

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
