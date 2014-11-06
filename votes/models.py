from django.db import models
from django.db.models import F
from django.db.models.signals import post_save, post_delete
from django import forms
from django.dispatch import receiver
from rulez import registry

from submissions.models import Submission


class Vote(models.Model):

    class Meta:
        db_table = 'votes'
        unique_together = ('submission', 'voted_by')

    THUMBS_UP = 1
    FEATURE = 10

    VOTE_CHOICES = (
        (THUMBS_UP, 'Thumbs Up'),
        (FEATURE,   'Feature'),
    )

    submission = models.ForeignKey(Submission)
    voted_by = models.ForeignKey('auth.User')
    status = models.IntegerField(choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        if self.submission_id:
            submission = '%s' % self.submission
        else:
            submission = 'unset'

        if self.status:
            status = self.get_status_display()
        else:
            status = 'none'
        return '%s :: %s' % ( submission, status )

    def __str__(self):
        return unicode(self).encode('utf-8')

    # Allow authenticated users to delete their own votes
    def can_delete(self, user=None):
        if (user and user.is_authenticated() and 
            self.voted_by.id == user.id):
            return True
        return False

    # Return the votes made by the given user for the given
    # submission or exhibition.
    # If no user given, returns none.
    @classmethod
    def can_delete_queryset(cls, qs=None, user=None, exhibition=None, submission=None):
        if not qs:
            qs = cls.objects
        if user and user.is_authenticated():
            qs = qs.filter(voted_by=user)

            if submission:
                qs = qs.filter(submission=submission)
            elif exhibition:
                qs = qs.filter(submission__exhibition=exhibition)
        else:
            qs = qs.none()
        return qs

registry.register('can_delete', Vote)

@receiver(post_save, sender=Vote)
def post_save(sender, instance=None, created=False, **kwargs):
    if created and (instance.status == Vote.THUMBS_UP):
        instance.submission.score = F('score') + 1
        instance.submission.save()

@receiver(post_delete, sender=Vote)
def post_delete(sender, instance=None, **kwargs):
    if instance.status == Vote.THUMBS_UP:
        instance.submission.score = F('score') - 1
        instance.submission.save()


class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['submission', 'status']
