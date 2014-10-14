from django.test import TestCase
from django.db import IntegrityError

from artwork.models import Artwork, ArtworkForm
from gallery.tests import UserSetUp

class ArtworkTests(TestCase):
    """Artwork model tests."""

    def test_str(self):
        
        artwork = Artwork(title='Empty code', code='// code goes here')

        self.assertEquals(
            str(artwork),
            'Empty code'
        )

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
