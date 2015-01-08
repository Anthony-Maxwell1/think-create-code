from django.db import models
from django.db.models import Q
from django.conf import settings
from django import forms
from django.core.urlresolvers import reverse
from rulez import registry


class Artwork(models.Model):
    class Meta:
        db_table = 'artwork'

    title = models.CharField(max_length=500)
    code = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    shared = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)


    def __unicode__(self):
        return self.title

    def __str__(self):
        return unicode(self).encode('utf-8')

    def get_absolute_url(self):
        return reverse('artwork-view', kwargs={'pk': self.id})

    # Only authors can see un-shared artwork
    def can_see(self, user=None):
        if (self.shared > 0 or 
            (user and user.is_authenticated() and 
             (self.author.id == user.id))):
            return True
        return False

    # Only allow authors to save artwork
    def can_save(self, user=None):
        if (user and user.is_authenticated() and 
             (self.author.id == user.id)):
            return True
        return False

    # Return queryset filtered to shared or own artwork
    @classmethod
    def can_see_queryset(cls, qs=None, user=None):
        if not qs:
            qs = cls.objects

        # Authenticated users can see shared or own artwork
        if (user and user.is_authenticated()):
            return qs.filter(Q(author__exact=user.id) | Q(shared__gt=0))

        # Public can only see shared artwork
        else:
            return qs.filter(Q(shared__gt=0))

    # Return queryset filtered to own artwork
    @classmethod
    def can_save_queryset(cls, qs=None, user=None):
        if not qs:
            qs = cls.objects
        if (user and user.is_authenticated()):
            # Authors can submit any artwork
            return qs.filter(author__exact=user.id)
        else:
            return qs.none()


registry.register('can_see', Artwork)
registry.register('can_save', Artwork)


class ArtworkForm(forms.ModelForm):
    class Meta:
        model = Artwork
        fields = ['title', 'code']
