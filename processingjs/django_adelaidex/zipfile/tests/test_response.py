# -*- coding: utf-8 -*-
from django.test import TestCase
from zipfile import ZipFile
from StringIO import StringIO
from exceptions import UnicodeEncodeError, UnboundLocalError
from django.test.client import RequestFactory
from django.conf import settings
import os

from django_adelaidex.zipfile.response import ZipFileResponse, ZIP_DEFLATED
from django_adelaidex.zipfile.mixins import ZipFileViewMixin


class ZipFileTest(TestCase):

    def setUp(self):
        super(ZipFileTest, self).setUp()
        self.files = {
            'birth.txt': 'hello world!',
            'death.txt': 'goodbye, cruel world!',
            'reincarnation.txt': 'i remember you!',
            'love.txt': u'i ❤ you',
        }
        self.output = StringIO()
        self.zipfile = ZipFile(self.output, mode='w', compression=ZIP_DEFLATED)


class ZipFileResponseTest(ZipFileTest):

    def test_default_response(self):
        response = ZipFileResponse()

        for fn, content in self.files.iteritems():
            response.append(fn, content)
            self.zipfile.writestr(fn, content.encode(response._content_encoding))

        response.close()
        self.zipfile.close()

        headers = "Content-Type: application/octet-stream\r\nContent-Disposition: attachment; filename=file.zip\r\n\r\n"
        self.assertEqual('%s' % response, '%s%s' % (headers, self.output.getvalue()))
    
    def test_response_filename(self):
        response = ZipFileResponse(filename='otherfile')

        for fn, content in self.files.iteritems():
            response.append(fn, content)
            self.zipfile.writestr(fn, content.encode(response._content_encoding))

        response.close()
        self.zipfile.close()

        headers = "Content-Type: application/octet-stream\r\nContent-Disposition: attachment; filename=otherfile\r\n\r\n"
        self.assertEqual('%s' % response, '%s%s' % (headers, self.output.getvalue()))

    def test_response_no_encoding(self):
        response = ZipFileResponse(content_encoding=None)

        for fn, content in self.files.iteritems():
            # writestr fails for unencoded unicode content
            if fn == 'love.txt':
                with self.assertRaises(UnicodeEncodeError):
                    response.append(fn, content)
            else:
                response.append(fn, content)
                self.zipfile.writestr(fn, content)

        response.close()
        self.zipfile.close()

        headers = "Content-Type: application/octet-stream\r\nContent-Disposition: attachment; filename=file.zip\r\n\r\n"
        self.assertEqual('%s' % response, '%s%s' % (headers, self.output.getvalue()))


class ZipFileViewMixinTest(ZipFileTest):

    def setUp(self):
        super(ZipFileViewMixinTest, self).setUp()
    
        with self.assertRaises(UnboundLocalError):
            view = ZipFileViewMixin()

        # Have to jerry-rig the class so we can use it for testing
        ZipFileViewMixin.object_template_name = 'template.html'
        ZipFileViewMixin.object_template_dirs = [os.path.dirname(os.path.abspath(__file__))]

        def get_context_object_name(*args, **kwargs):
            return 'foo'
        ZipFileViewMixin.get_context_object_name = get_context_object_name

        rf = RequestFactory()
        _orig_init = ZipFileViewMixin.__init__
        def init(mixin, *args, **kwargs):
            _orig_init(mixin, *args, **kwargs)
            mixin.request = rf.get('/')
        ZipFileViewMixin.__init__ = init

    def tearDown(self):
        # Undo the jerry-rigging we just did
        ZipFileViewMixin.object_template_name = None
        ZipFileViewMixin.object_template_dirs = None


    class MockObject(object):
        class MockMeta(object):
            def __init__(self):
                self.model_name = 'foo_model'

        def __init__(self, pk, content=''):
            self.pk = pk
            self.content = content
            self._meta = self.MockMeta()

    def test_render_object(self):

        # Have to stub the mixin instance
        view = ZipFileViewMixin()

        pk = 0
        fn = 'love.txt'
        content = self.files[fn]
        obj = self.MockObject(pk, content)

        fn = ZipFileViewMixin.object_filename % pk
        # have to append a newline to handle template formatting guff
        content = "%s\n" % content.encode('utf-8')
        self.zipfile.writestr(fn, content)

        response = view.render_to_response({'object': obj})
        self.zipfile.close()

        headers = "Content-Type: application/octet-stream\r\nContent-Disposition: attachment; filename=download.zip\r\n\r\n"
        self.assertEqual('%s' % response, '%s%s' % (headers, self.output.getvalue()))

    def test_render_list(self):

        # Have to stub the mixin instance
        view = ZipFileViewMixin()
        object_list = []

        pk = 0
        for fn, content in self.files.iteritems():
            object_list.append(self.MockObject(pk, content))

            fn = ZipFileViewMixin.object_filename % pk
            # have to append a newline to handle template formatting guff
            content = "%s\n" % content.encode('utf-8')

            self.zipfile.writestr(fn, content)
            pk += 1

        response = view.render_to_response({'object_list': object_list})
        self.zipfile.close()

        headers = "Content-Type: application/octet-stream\r\nContent-Disposition: attachment; filename=download.zip\r\n\r\n"
        self.assertEqual('%s' % response, '%s%s' % (headers, self.output.getvalue()))
