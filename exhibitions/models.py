from django.db import models
from django import forms
from django.utils import timezone

from artwork.models import Artwork


class Exhibition(models.Model):
    class Meta:
        db_table = 'exhibitions'

    title = models.CharField(max_length=500)
    description = models.TextField()
    author = models.ForeignKey('auth.User')
    released_at = models.DateTimeField(verbose_name="release date", default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.title

    def __str__(self):
        return unicode(self).encode('utf-8')


class ExhibitionForm(forms.ModelForm):
    class Meta:
        model = Exhibition
        fields = ['title', 'description', 'released_at',]
