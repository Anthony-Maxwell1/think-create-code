import os
from django.views.generic import CreateView, DeleteView
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

from gallery.views import LoggedInMixin, ObjectHasPermMixin
from submissions.models import Submission, SubmissionForm
from artwork.models import Artwork
from exhibitions.models import Exhibition


class SubmissionView(object):
    model = Submission
    form_class = SubmissionForm
    template_dir = 'submissions'

    @classmethod
    def prepend_template_path(cls, *argv):
        return os.path.join(cls.template_dir, *argv)

    def get_success_url(self):
        return reverse('exhibition-view', kwargs={'pk': self.object.exhibition.id})


class CreateSubmissionView(LoggedInMixin, SubmissionView, CreateView):

    template_name = SubmissionView.prepend_template_path('add.html')

    def dispatch(self, request, *args, **kwargs):
        method = request.method.lower()
        if (method == 'post') or (method == 'put'):
            return super(CreateSubmissionView, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def form_valid(self, form):

        # Throw exception if user tries to submit invalid choices
        if form.instance.can_save(self.request.user):
            # Set submitted_by to current user
            form.instance.submitted_by = self.request.user
            return super(CreateSubmissionView, self).form_valid(form)
        raise PermissionDenied

    def get_context_data(self, **kwargs):

        context = super(CreateSubmissionView, self).get_context_data(**kwargs)

        # Restrict list of artwork the current user can submit to
        context['form'].fields['artwork'].queryset = Artwork.can_submit_queryset( 
            context['form'].fields['artwork'].queryset,
            self.request.user)

        # Restrict to specific artwork if given
        artwork_id = self.kwargs.get('artwork')
        if artwork_id:
            context['form'].fields['artwork'].queryset =\
                context['form'].fields['artwork'].queryset.filter(id=artwork_id)

        # Restrict list of exhibitions the current user can see
        context['form'].fields['exhibition'].queryset = Exhibition.can_see_queryset( 
            context['form'].fields['exhibition'].queryset,
            self.request.user)

        return context


class DeleteSubmissionView(LoggedInMixin, ObjectHasPermMixin, SubmissionView, DeleteView):

    template_name = SubmissionView.prepend_template_path('delete.html')
    user_perm = 'can_save'
    raise_exception = True

    def get_success_url(self):
        return reverse('artwork-view', kwargs={'pk': self.object.artwork_id})
