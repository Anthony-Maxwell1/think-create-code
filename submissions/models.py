from django.db import models
from django import forms
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from django.forms.widgets import Select
from itertools import chain
from rulez import registry

from artwork.models import Artwork
from exhibitions.models import Exhibition


class Submission(models.Model):

    class Meta:
        unique_together = ('exhibition', 'artwork')

    exhibition = models.ForeignKey(Exhibition)
    artwork = models.ForeignKey(Artwork)
    submitted_by = models.ForeignKey('auth.User')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return '%s :: %s' % ( self.exhibition, self.artwork )

    def __str__(self):
        return unicode(self).encode('utf-8')

    # Allow authenticated staff, superusers, or authors to submit artwork to exhibitions
    # they can see
    def can_save(self, user=None):
        if (user and user.is_authenticated and 
           (user.is_superuser or user.is_staff or
            (self.artwork.author.id == user.id)) and
            self.exhibition.can_see(user)):
            return True
        return False

registry.register('can_save', Submission)


class SelectOneOrNoneWidget(Select):
    '''Select Widget that checks the number of choices available before
       rendering the input element.
       If 0 choices, shows error.
       If 1 choice, shows just that choice.'''

    def render(self, name, value, attrs=None, choices=()):

        num_choices = len(self.choices.queryset)
        if num_choices > 1:
            return super(SelectOneOrNoneWidget, self).render(name, value, attrs, choices)

        output = []
        # If there's no choices, show error
        if num_choices == 0:
            output.append('<div>Sorry, no choices available.</div>')

        else:
            for option_value, option_label in chain(self.choices, choices):
                # skip field.empty_label
                if option_value:
                    output.append(format_html('<input type="{0}" name="{1}" value="{2}" />{3}',
                        'hidden',
                        name,
                        option_value,
                        force_text(option_label)))

        return mark_safe('\n'.join(output))


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['exhibition', 'artwork']
        widgets = {
            'exhibition': SelectOneOrNoneWidget,
            'artwork': SelectOneOrNoneWidget,
        }
