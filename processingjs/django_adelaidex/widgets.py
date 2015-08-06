from django.forms.widgets import Widget, Select, RadioSelect
from django.forms.utils import flatatt
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.conf import settings
from itertools import chain
import pytz


class SelectOneOrNoneWidget(RadioSelect):

    def __init__(self, attrs=None):
        super(SelectOneOrNoneWidget, self).__init__(attrs)
        is_required = True

    '''Select Widget that checks the number of choices available before
       rendering the input element.
       If 0 choices, shows error.
       If 1 choice, shows just that choice.'''

    def render(self, name, value, attrs=None, choices=()):

        output = []
        num_choices = len(self.choices.queryset)
        if num_choices > 1:
            for option_value, option_label in chain(self.choices, choices):
                # skip field.empty_label
                if option_value:
                    output.append(format_html(
                        '<li><input type="{0}" name="{1}" value="{2}" id="{1}-{2}" />'
                        ' <label for="{1}-{2}">{3}</label></li>',
                        'radio',
                        name,
                        option_value,
                        force_text(option_label)))

        # If there's no choices, show error
        elif num_choices == 0:
            output.append('<div>Sorry, no choices available.</div>')

        else:
            for option_value, option_label in chain(self.choices, choices):
                # skip field.empty_label
                if option_value:
                    output.append(format_html('<input type="{0}" name="{1}" value="{2}" id="{1}-{2}" />{3}',
                        'hidden',
                        name,
                        option_value,
                        force_text(option_label)))

        return mark_safe('\n'.join(output))


class SelectTimeZoneWidget(Select):

    def render(self, name, value, attrs=None, choices=()):

        timezones = pytz.common_timezones
        choices = []
        for tz in timezones:
            choices.append((tz, tz))

        if not value:
            value = settings.TIME_ZONE

        return super(SelectTimeZoneWidget, self).render(name, value, attrs, choices)
