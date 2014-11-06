from django.test import TestCase
from django.template.base import Template
from django.template.context import Context

# ref https://github.com/django/django/blob/master/django/contrib/flatpages/tests/test_templatetags.py
class DictFilterTests(TestCase):

    def setUp(self):
        self.dictionary = {'a': 1, 'b': 2}

    def test_get_key(self):
        t = Template('{% load dict_filters %}{{ dict|get:"a" }}')
        c = Context({"dict": self.dictionary})
        output = t.render(c)
        self.assertEqual(output, "1")

    def test_get_key_var(self):
        t = Template('{% load dict_filters %}{% with key="a" %}{{ dict|get:key }}{% endwith %}')
        c = Context({"dict": self.dictionary})
        output = t.render(c)
        self.assertEqual(output, "1")

    def test_get_key_not_found(self):
        t = Template('{% load dict_filters %}{{ dict|get:"k" }}')
        c = Context({"dict": self.dictionary})
        output = t.render(c)
        self.assertEqual(output, "")

    def test_bad_dict(self):
        t = Template('{% load dict_filters %}{{ dict|get:"k" }}')
        c = Context({"dict": 'abc'})
        output = t.render(c)
        self.assertEqual(output, "")
