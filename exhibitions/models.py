from django.db import models
from django import forms
from django.utils import timezone
from rulez import registry

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

    def _released_yet(self):
        return (self.released_at <= timezone.now())

    released_yet = property(_released_yet)

    def can_see(self, user):
        if self.can_save(user) or self.released_yet:
            return True
        return False

    @classmethod
    def can_save(cls, user):
        if user and user.is_authenticated and (user.is_superuser or user.is_staff):
            return True
        return False

    # Have to be have can_save permission to see exhibitions prior to release date
    @classmethod
    def restrict_queryset(cls, qs, user):
        if cls.can_save(user):
            return qs
        return qs.filter(released_at__lte=timezone.now())


registry.register('can_see', Exhibition)
registry.register('can_save', Exhibition)


class ExhibitionForm(forms.ModelForm):
    class Meta:
        model = Exhibition
        fields = ['title', 'description', 'released_at',]
