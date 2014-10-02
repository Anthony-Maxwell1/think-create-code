from django.db import models
from django import forms
from rulez import registry


class Artwork(models.Model):
    class Meta:
        db_table = 'artwork'

    title = models.CharField(max_length=500)
    code = models.TextField()
    author = models.ForeignKey('auth.User')
    shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)


    def __unicode__(self):
        return self.title

    def __str__(self):
        return unicode(self).encode('utf-8')

    # Allow authenticated superusers or authors to save artwork
    def can_save(self, user):
        if user.is_authenticated and (user.is_superuser or (self.author.id == user.id)):
            return True
        return False

registry.register('can_save', Artwork)


# n.b. can also do the reverse:
# def user_can_save(user, obj):
#     ...
# User.add_to_class('can_save', user_can_save)
# registry.register('can_save', User)


class ArtworkForm(forms.ModelForm):
    class Meta:
        model = Artwork
        fields = ['title', 'code']

    # Grab the request object, so we can assign the author
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        return super(ArtworkForm, self).__init__(*args, **kwargs)

    # Override author with the request user
    def save(self, *args, **kwargs):
        kwargs['commit']=False
        obj = super(ArtworkForm, self).save(*args, **kwargs)

        # FIXME : don't override an existing user.  Tried
        #   and obj.author is None  DoesNotExist exception : Artwork has no author.
        if self.request:
            obj.author = self.request.user

        obj.save()
        return obj
