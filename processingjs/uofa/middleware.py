# https://docs.djangoproject.com/en/1.7/topics/i18n/timezones/#selecting-the-current-time-zone
import pytz
from django.utils import timezone

class TimezoneMiddleware(object):
    '''Use the currently-authenticated user's configured timezone
       as the current timezone to display all dates/times.
      
       If no timezone configured, use the default.'''
    def process_request(self, request):
        timezone.deactivate()
        if request.user and request.user.is_authenticated():
            tzname = request.user.time_zone
            if tzname:
                timezone.activate(pytz.timezone(tzname))
        return None


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
