# https://docs.djangoproject.com/en/1.7/topics/i18n/timezones/#selecting-the-current-time-zone
import pytz
from django.utils import timezone

class TimezoneMiddleware(object):
    def process_request(self, request):
        timezone.deactivate()
        if request.user and request.user.is_authenticated():
            tzname = request.user.time_zone
            if tzname:
                timezone.activate(pytz.timezone(tzname))
        return None
