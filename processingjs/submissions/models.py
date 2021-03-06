from django.db import models
from django.db.models import Q
from django.conf import settings
from django import forms
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rulez import registry

from django_adelaidex.lti.models import Cohort
from artwork.models import Artwork
from exhibitions.models import Exhibition
from django_adelaidex.util.widgets import SelectOneOrNoneWidget


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

    def _disqus_identifier(self):
        return settings.ADELAIDEX_LTI_DISQUS['IDENTIFIER'] % self.artwork.id

    disqus_identifier = property(_disqus_identifier)

    def get_absolute_url(self):
        return self.artwork.get_absolute_url()

    # Allow anyone to see any submission
    def can_see(self, user=None):
        return True

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

    # Anyone can see any submission, but in list mode, 
    # we tailer what gets shown by exhibition or cohort.
    @classmethod
    def can_see_queryset(cls, qs=None, user=None, exhibition=None):
        if not qs:
            qs = cls.objects

        if exhibition:
            if isinstance(exhibition, Exhibition):
                exhibition = exhibition.id
            qs = qs.filter(exhibition_id=exhibition)
        else:
           cohort = Cohort.objects.get_current(user=user)
           qs = qs.filter(Q(exhibition__cohort__isnull=True) | Q(exhibition__cohort=cohort))

        return qs

registry.register('can_see', Submission)
registry.register('can_save', Submission)
registry.register('can_vote', Submission)


@receiver(post_save, sender=Submission)
def post_save(sender, instance=None, **kwargs):
    '''Update artwork.shared to submission id'''
    if instance:
        from artwork.models import Artwork
        Artwork.objects.filter(id__exact=instance.artwork_id).update(shared=instance.id)


@receiver(post_delete, sender=Submission)
def post_delete(sender, instance=None, **kwargs):
    '''Decrement artwork.shared, and delete existing votes.'''
    if instance:
        from artwork.models import Artwork
        Artwork.objects.filter(id__exact=instance.artwork_id).update(shared=0)


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['exhibition', 'artwork']
        widgets = {
            'exhibition': SelectOneOrNoneWidget,
            'artwork': SelectOneOrNoneWidget,
        }
