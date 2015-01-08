import os
from django.views.generic import CreateView, DeleteView
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

from uofa.views import TemplatePathMixin, PostOnlyMixin, LoggedInMixin, ObjectHasPermMixin
from submissions.models import Submission, SubmissionForm
from artwork.models import Artwork
from exhibitions.models import Exhibition


class SubmissionView(TemplatePathMixin):
    model = Submission
    form_class = SubmissionForm
    template_dir = 'submissions'

    def get_success_url(self):
        return reverse('exhibition-view', kwargs={'pk': self.object.exhibition.id})


class CreateSubmissionView(PostOnlyMixin, LoggedInMixin, SubmissionView, CreateView):

    template_name = SubmissionView.prepend_template_path('add.html')

    def form_valid(self, form):

        # Throw exception if user tries to submit invalid choices
        if form.instance.can_save(self.request.user):
            # Set submitted_by to current user
            form.instance.submitted_by = self.request.user
            return super(CreateSubmissionView, self).form_valid(form)
        raise PermissionDenied

    def get_context_data(self, **kwargs):

        context = super(CreateSubmissionView, self).get_context_data(**kwargs)

        # Restrict list of artwork the current user can submit
        context['form'].fields['artwork'].queryset = Artwork.can_save_queryset( 
            context['form'].fields['artwork'].queryset,
            self.request.user)

        # Restrict to specific artwork if given
        artwork_id = self.kwargs.get('artwork')
        exclude_exhibitions = []
        if artwork_id:
            context['form'].fields['artwork'].queryset =\
                context['form'].fields['artwork'].queryset.filter(id=artwork_id)

            # Fetch the exhibitions this artwork has already been submitted to
            exclude_exhibitions = Submission.objects.filter(
                artwork__exact=artwork_id).order_by('-created_at').values_list('exhibition', flat=True)

        # Restrict list of exhibitions the current user can see,
        # and exclude exhibitions this artwork has already been submitted to
        context['form'].fields['exhibition'].queryset = Exhibition.can_see_queryset( 
            context['form'].fields['exhibition'].queryset,
            self.request.user).exclude(id__in=exclude_exhibitions)
        
        return context


class DeleteSubmissionView(LoggedInMixin, ObjectHasPermMixin, SubmissionView, DeleteView):

    template_name = SubmissionView.prepend_template_path('delete.html')
    user_perm = 'can_save'
    raise_exception = True

    def get_success_url(self):
        return reverse('artwork-view', kwargs={'pk': self.object.artwork_id})
