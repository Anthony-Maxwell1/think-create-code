from django.db import models
from django.conf import settings
from django import forms
from django.db.models.signals import pre_save, pre_delete
from django.db.models import F
from django.dispatch import receiver
from rulez import registry

from artwork.models import Artwork
from exhibitions.models import Exhibition
from uofa.widgets import SelectOneOrNoneWidget


class Submission(models.Model):

    class Meta:
        unique_together = ('exhibition', 'artwork')

    exhibition = models.ForeignKey(Exhibition)
    artwork = models.ForeignKey(Artwork)
    score = models.IntegerField(default=0)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return '%s :: %s' % ( self.exhibition, self.artwork )

    def __str__(self):
        return unicode(self).encode('utf-8')

    # Allow authenticated authors to submit their artwork 
    # to exhibitions they can see
    def can_save(self, user=None):
        if (user and user.is_authenticated() and
            (self.artwork.author.id == user.id) and
            self.exhibition.can_see(user)):
            return True
        return False

    # Allow authenticated users to vote on any submission in an
    # exhibition they can see, and haven't voted on before
    def can_vote(self, user=None):
        from votes.models import Vote
        if (user and user.is_authenticated() and
            self.exhibition.can_see(user) and
            not Vote.can_delete_queryset(user=user, submission=self)):
            return True
        return False

registry.register('can_save', Submission)
registry.register('can_vote', Submission)


@receiver(pre_save, sender=Submission)
def pre_save(sender, instance=None, **kwargs):
    '''Increment artwork.shared counter'''
    if instance:
        from artwork.models import Artwork
        Artwork.objects.filter(id__exact=instance.artwork_id).update(shared=F('shared')+1)


@receiver(pre_delete, sender=Submission)
def pre_delete(sender, instance=None, **kwargs):
    '''Decrement artwork.shared counter, and delete existing votes.'''
    if instance:
        from artwork.models import Artwork
        Artwork.objects.filter(id__exact=instance.artwork_id).update(shared=F('shared')-1)

        from votes.models import Vote
        Vote.can_delete_queryset(submission=instance).delete()


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['exhibition', 'artwork']
        widgets = {
            'exhibition': SelectOneOrNoneWidget,
            'artwork': SelectOneOrNoneWidget,
        }
