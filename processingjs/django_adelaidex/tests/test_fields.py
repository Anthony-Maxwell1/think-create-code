from django.test import TestCase
from django_adelaidex.fields import NullableCharField


class NullableCharFieldTest(TestCase):
    def setUp(self):
        super(NullableCharFieldTest, self).setUp()
        self.ncf = NullableCharField()

    def test_to_python(self):
        self.assertEqual(self.ncf.to_python(None), '')
        self.assertEqual(self.ncf.to_python(''), '')
        self.assertEqual(self.ncf.to_python(0), '')
        self.assertEqual(self.ncf.to_python(1), 1)
        self.assertEqual(self.ncf.to_python('abc'), 'abc')

    def test_get_prep_value(self):
        self.assertEqual(self.ncf.get_prep_value(None), None)
        self.assertEqual(self.ncf.get_prep_value(''), None)
        self.assertEqual(self.ncf.get_prep_value(0), None)
        self.assertEqual(self.ncf.get_prep_value(1), 1)
        self.assertEqual(self.ncf.get_prep_value('abc'), 'abc')
