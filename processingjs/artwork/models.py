from django.db import models
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
    shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)


    def __unicode__(self):
        return self.title

    def __str__(self):
        return unicode(self).encode('utf-8')

    def get_absolute_url(self):
        return reverse('artwork-view', kwargs={'pk': self.id})

    # Allow authenticated staff, superusers or authors to delete artwork
    def can_delete(self, user=None):
        if (user and user.is_authenticated() and 
            (user.is_superuser or user.is_staff or 
             (self.author.id == user.id))):
            return True
        return False

    # Allow authenticated staff, superusers or authors to submit artwork
    def can_submit(self, user=None):
        return self.can_delete(user)

    # Only allow authors to edit artwork
    def can_edit(self, user=None):
        if (user and user.is_authenticated() and 
             (self.author.id == user.id)):
            return True
        return False

    # Return queryset filtered to own artwork
    @classmethod
    def can_submit_queryset(cls, qs, user=None):
        if (user and user.is_authenticated()):
            # Staff and superusers can submit any artwork
            if (user.is_superuser or user.is_staff):
                return qs

            # Everyone else can submit the artwork they own
            return qs.filter(author__exact=user.id)
        else:
            return qs.none()


registry.register('can_edit', Artwork)
registry.register('can_delete', Artwork)
registry.register('can_submit', Artwork)


class ArtworkForm(forms.ModelForm):
    class Meta:
        model = Artwork
        fields = ['title', 'code']
