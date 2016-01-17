from django.db import models
from django.db.models import Q
from django.db.models.signals import post_init, post_save, post_delete
from django.conf import settings
from django.utils import timezone
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from rulez import registry
from database_files.models import File
from django_adelaidex.lti.models import Cohort


class Exhibition(models.Model):
    class Meta:
        db_table = 'exhibitions'

    title = models.CharField(max_length=500)
    description = models.TextField()
    image = models.ImageField(upload_to='not required',
        null=True, blank=True, default=None,
        help_text=_('Max file size 4MB.'),
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    cohort = models.ForeignKey(Cohort, null=True, blank=True, default=None)
    released_at = models.DateTimeField(verbose_name="release date",
        null=True, blank=True, default=None,
        help_text=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    # Store the original image field, to track changes on save
    __init_image = None

    def __unicode__(self):
        return self.title

    def __str__(self):
        return unicode(self).encode('utf-8')

    def _released_yet(self):
        return (self.released_at is None) or (self.released_at <= timezone.now())

    released_yet = property(_released_yet)

    def can_see(self, user=None):
        if self.can_save(user):
            return True
        elif self.released_yet:
            if self.cohort is None:
                return True
            else:
                # Show exhibitions for the user's cohort
                cohort = Cohort.objects.get_current(user)
                return self.cohort == cohort
        return False

    @classmethod
    def can_save(cls, user=None):
        if user and (user.is_superuser or user.is_staff):
            return True
        return False

    # Have to have can_save permission to see exhibitions prior to release date.
    # Also, filter out any exhibitions not intended for the current cohort.
    @classmethod
    def can_see_queryset(cls, qs=None, user=None):
        if not qs:
            qs = cls.objects

        if not cls.can_save(user):
            qs = qs.filter(Q(released_at__isnull=True) | Q(released_at__lte=timezone.now()))

        # Show "all cohorts" and "current cohort" exhibitions to non-superusers
        if not user or not user.is_authenticated() or not user.is_superuser:
            cohort = Cohort.objects.get_current(user)
            qs = qs.filter(Q(cohort__isnull=True) | Q(cohort=cohort))

        return qs


registry.register('can_see', Exhibition)
registry.register('can_save', Exhibition)


@receiver(post_init, sender=Exhibition)
def post_init(sender, instance=None, **kwargs):
    '''Store initial image, to detect changes in post_save, post_delete'''
    if instance:
        instance.__init_image = instance.image

@receiver(post_delete, sender=Exhibition)
def post_delete(sender, instance=None, **kwargs):
    '''Delete orphan image, if any'''
    if instance:
        if instance.__init_image:
            instance.__init_image.storage.delete(instance.__init_image.name)

@receiver(post_save, sender=Exhibition)
def post_save(sender, instance=None, **kwargs):
    '''Delete orphan image, if any'''
    if instance:
        if instance.__init_image and (
          not instance.image 
          or (instance.image != instance.__init_image)):
            instance.__init_image.storage.delete(instance.__init_image.name)


class ExhibitionForm(forms.ModelForm):
    class Meta:
        model = Exhibition
        fields = ['title', 'description', 'image', 'cohort', 'released_at',]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ExhibitionForm, self).__init__(*args, **kwargs)

        cohort = self.fields.get('cohort')
        cohort.empty_label = _("Shared by all cohorts")

        if self.request and self.request.user:
            current_cohort = Cohort.objects.get_current(self.request.user)
            if current_cohort and current_cohort.id:
                self.initial['cohort'] = current_cohort.id
