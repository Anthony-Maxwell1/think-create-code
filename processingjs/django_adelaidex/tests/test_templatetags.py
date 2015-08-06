from django.test import TestCase
from django.template.base import Template
from django.template.context import Context
from django.core.paginator import Paginator
import re

from django_adelaidex.templatetags import pagination
from django_adelaidex.lti.models import User

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


class PaginationTests(TestCase):

    def setUp(self):
        self.perpage = 10

    def test_empty_pagination(self):

        paginator = Paginator(User.objects.all(), per_page=self.perpage)
        page = paginator.page(1)
        context = pagination.pagination(page)
        self.assertEqual(context['num_pages'], 1)
        self.assertEqual(context['page'], page)
        self.assertEqual(context['begin'], [1])
        self.assertEqual(context['middle'], [])
        self.assertEqual(context['end'], [])

    def test_single_pagination(self):

        User.objects.create(username="user")
        paginator = Paginator(User.objects.all(), per_page=self.perpage)
        page = paginator.page(1)
        context = pagination.pagination(page)
        self.assertEqual(context['num_pages'], 1)
        self.assertEqual(context['page'], page)
        self.assertEqual(context['begin'], [1])
        self.assertEqual(context['middle'], [])
        self.assertEqual(context['end'], [])

    def test_pagination_begin(self):

        numpages = 100
        begin_pages = 2
        end_pages = 4
        before_current_pages = 6
        after_current_pages = 8

        for x in range(0, numpages * self.perpage):
            User.objects.create(username="user%s" % x)

        paginator = Paginator(User.objects.all(), per_page=self.perpage)

        for x in range(1, begin_pages+1):
            page = paginator.page(x)
            context = pagination.pagination(page, begin_pages, end_pages, before_current_pages, after_current_pages)

            self.assertEqual(context['num_pages'], numpages)
            self.assertEqual(context['page'], page)
            self.assertEqual(context['begin'], range(1, min(before_current_pages + after_current_pages, numpages)+1))
            self.assertEqual(context['middle'], [])
            self.assertEqual(context['end'], range(numpages - end_pages + 1, numpages+1))

    def test_pagination_middle(self):

        numpages = 100
        begin_pages = 3
        end_pages = 6
        before_current_pages = 5
        after_current_pages = 6

        for x in range(0, numpages * self.perpage):
            User.objects.create(username="user%s" % x)

        paginator = Paginator(User.objects.all(), per_page=self.perpage)

        for x in range(numpages/2, numpages/2 + before_current_pages):
            page = paginator.page(x)
            context = pagination.pagination(page, begin_pages, end_pages, before_current_pages, after_current_pages)

            self.assertEqual(context['num_pages'], numpages)
            self.assertEqual(context['page'], page)
            self.assertEqual(context['begin'], range(1, begin_pages+1))
            self.assertEqual(context['middle'], range(max(x-before_current_pages, 0), x+after_current_pages+1))
            self.assertEqual(context['end'], range(numpages - end_pages + 1, numpages+1))

    def test_pagination_end(self):

        numpages = 100
        begin_pages = 6
        end_pages = 8
        before_current_pages = 3
        after_current_pages = 4

        for x in range(0, numpages * self.perpage):
            User.objects.create(username="user%s" % x)

        paginator = Paginator(User.objects.all(), per_page=self.perpage)

        for x in range(numpages - end_pages - 1, numpages+1):
            page = paginator.page(x)
            context = pagination.pagination(page, begin_pages, end_pages, before_current_pages, after_current_pages)

            self.assertEqual(context['num_pages'], numpages)
            self.assertEqual(context['page'], page)
            self.assertEqual(context['begin'], range(1, begin_pages+1))
            self.assertEqual(context['middle'], [])
            self.assertEqual(context['end'], range(numpages - end_pages + 1, numpages+1))

    def test_pagination_collide(self):

        numpages = 10
        begin_pages = 3
        end_pages = 3
        before_current_pages = 3
        after_current_pages = 3

        for x in range(0, numpages * self.perpage):
            User.objects.create(username="user%s" % x)

        paginator = Paginator(User.objects.all(), per_page=self.perpage)

        for x in range(1, begin_pages+1):
            page = paginator.page(x)
            context = pagination.pagination(page, begin_pages, end_pages, before_current_pages, after_current_pages)

            self.assertEqual(context['num_pages'], numpages)
            self.assertEqual(context['page'], page)
            self.assertEqual(context['begin'], range(1, min(before_current_pages + after_current_pages, numpages)+1))
            self.assertEqual(context['middle'], [])
            self.assertEqual(context['end'], range(numpages - end_pages + 1, numpages+1))

        for x in range(numpages/2, numpages/2 + before_current_pages):
            page = paginator.page(x)
            context = pagination.pagination(page, begin_pages, end_pages, before_current_pages, after_current_pages)

            self.assertEqual(context['num_pages'], numpages)
            self.assertEqual(context['page'], page)
            self.assertEqual(context['begin'], range(1, begin_pages+1))
            self.assertEqual(context['middle'], [])
            self.assertEqual(context['end'], range(max(numpages - before_current_pages - after_current_pages, 1), numpages+1))

        for x in range(numpages - end_pages - 1, numpages+1):
            page = paginator.page(x)
            context = pagination.pagination(page, begin_pages, end_pages, before_current_pages, after_current_pages)

            self.assertEqual(context['num_pages'], numpages)
            self.assertEqual(context['page'], page)
            self.assertEqual(context['begin'], range(1, begin_pages+1))
            self.assertEqual(context['middle'], [])
            self.assertEqual(context['end'], range(max(numpages - before_current_pages - after_current_pages, 1), numpages+1))

class PaginationIntegrationTests(TestCase):

    def setUp(self):
        self.perpage = 10

    def test_empty_page(self):
        paginator = Paginator(User.objects.all(), per_page=self.perpage)

        t = Template('{% load pagination %}{% pagination page_obj %}')
        c = Context({"page_obj": paginator.page(1)})
        output = t.render(c)
        regex = re.compile(r'^\s*$', re.MULTILINE)
        self.assertRegexpMatches(output, regex)

    def test_single_page_template(self):
        for x in range(0, self.perpage):
            User.objects.create(username="user%s" % x)

        paginator = Paginator(User.objects.all(), per_page=self.perpage)

        t = Template('{% load pagination %}{% pagination page_obj %}')
        c = Context({"page_obj": paginator.page(1)})
        output = t.render(c)
        regex = re.compile(r'^\s*$', re.MULTILINE)
        self.assertRegexpMatches(output, regex)

    def test_three_page_template(self):
        for x in range(0, 3 * self.perpage):
            User.objects.create(username="user%s" % x)

        paginator = Paginator(User.objects.all(), per_page=self.perpage)

        t = Template('{% load pagination %}{% pagination page_obj %}')
        c = Context({"page_obj": paginator.page(1)})
        output = t.render(c)

        # Remove newlines for simplicity
        output = output.replace('\n', '')

        self.assertEquals(output, r'<div class="pagination-centered">'
            r'<ul class="pagination" role="menubar" aria-label="Pagination">'
            r''
            r'<li class="unavailable" aria-disabled="true"><a'
            r'><i class="fa fa-chevron-left"></i> Previous</a></li>'
            r''
            r''
            r'<li class="current"><a href=""'
            r'>1</a></li>'
            r''
            r'<li ><a href="?page=2"'
            r'>2</a></li>'
            r''
            r'<li ><a href="?page=3"'
            r'>3</a></li>'
            r''
            r''
            r''
            r''
            r''
            r''
            r'<li><a href="?page=2" title="next page"'
            r'>Next <i class="fa fa-chevron-right"></i></a></li>'
            r'</ul>'
            r'</div>')
