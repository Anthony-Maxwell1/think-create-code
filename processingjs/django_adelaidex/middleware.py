# https://djangosnippets.org/snippets/1731/
import traceback
from django.core.exceptions import PermissionDenied
from django.http import Http404

class WsgiLogErrors(object):
    '''Log all but the omitted exceptions w tracebacks to web server error_log via wsgi.errors.'''

    omit_exceptions = [
        PermissionDenied,   # caught by 403 handler
        Http404,            # caught by 404 handler
    ]

    def process_exception(self, request, exception):
        if not type(exception) in self.omit_exceptions:
            tb_text = traceback.format_exc()
            url = request.build_absolute_uri()
            request.META['wsgi.errors'].write('EXCEPTION raised serving: %s\n%s\n' % (url, str(tb_text)))


# https://djangosnippets.org/snippets/786/
from django.conf import settings

class P3PMiddleware(object):
    '''IE privacy headers'''

    def process_response(self, request, response):
        response[settings.P3P_HEADER_KEY] = settings.P3P_HEADER_VALUE
        return response
