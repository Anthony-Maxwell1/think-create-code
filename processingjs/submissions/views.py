import os
from django.views.generic import DetailView, ListView, CreateView, DeleteView
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

from django_adelaidex.util.mixins import TemplatePathMixin, PostOnlyMixin, LoggedInMixin, ObjectHasPermMixin
from django_adelaidex.zipfile.mixins import ZipFileViewMixin
from submissions.models import Submission, SubmissionForm
from artwork.models import Artwork
from exhibitions.models import Exhibition
from gallery.views import ShareView
from votes.models import Vote


class SubmissionView(TemplatePathMixin):
    model = Submission
    form_class = SubmissionForm
    template_dir = 'submissions'


class SubmissionCodeView(SubmissionView, DetailView):
    template_name = SubmissionView.prepend_template_path('code.pde')
    content_type = 'text/plain'
    content_disposition = 'attachment;'
    #method_user_perm = { 'GET': 'can_see' }

    def render_to_response(self, context, **response_kwargs):
        response = super(SubmissionCodeView, self).render_to_response(
                context, **response_kwargs)
        response['Content-Disposition'] = self.content_disposition
        return response


class ShowSubmissionView(SubmissionView, DetailView):

    template_name = SubmissionView.prepend_template_path('view.html')

    def get_context_data(self, **kwargs):

        context = super(ShowSubmissionView, self).get_context_data(**kwargs)
        submission = self.get_object()

        # Include share url
        pk = submission.id
        context['share_url'] = ShareView.reverse_share_url(
            'submission-view',
            kwargs={'pk': pk})

        # Include in the current user's votes for this submission
        # as a dict of submission.id:vote
        votes = Vote.can_delete_queryset(user=self.request.user, submission=pk).all()
        context['votes'] = { v.submission_id:v for v in votes }

        context['DISQUS_IDENTIFIER'] = submission.disqus_identifier
        context['DISQUS_TITLE'] = '%s' % submission
        context['DISQUS_URL'] = self.request.build_absolute_uri(submission.get_absolute_url())

        return context


class ListSubmissionView(SubmissionView, ListView):
    '''Rendered by ShowExhibitionView'''
    template_name = SubmissionView.prepend_template_path('list.html')
    paginate_by = 12
    paginate_orphans = 4

    def __init__(self, show_download=True, *args, **kwargs):
        super(ListSubmissionView, self).__init__(*args, **kwargs)
        self.show_download = show_download

    def _get_exhibition_id(self):
        return self.kwargs.get('pk')

    def _get_order_by(self):
        return self.kwargs.get('order', '')

    def get_queryset(self):
        '''Show submissions to the given exhibition.'''
        qs = Submission.can_see_queryset(
                user=self.request.user, 
                exhibition=self._get_exhibition_id())

        # Show most recently submitted first
        order = self._get_order_by()
        if order == 'score':
            qs = qs.order_by('-score')
        else:
            qs = qs.order_by('-created_at')
        return qs

    def get_context_data(self, **kwargs):
        context = super(ListSubmissionView, self).get_context_data(**kwargs)
        context['order'] = self._get_order_by()

        # Include in the current user's votes for this exhibition
        # as a dict of submission.id:vote
        exhibition = self._get_exhibition_id()
        votes = Vote.can_delete_queryset(user=self.request.user, exhibition=exhibition).all()
        context['votes'] = { v.submission_id:v for v in votes }

        # Store url for downloading code zip file
        if self.show_download:
            url_name = self.request.resolver_match.url_name
            if not 'zip' in url_name:
                url_name = '%s-zip' % url_name
            kwargs = self.kwargs.copy()
            context['zip_file_url'] = reverse(url_name, kwargs=kwargs)

        return context


class ListSubmissionCodeZipFileView(ZipFileViewMixin, ListSubmissionView):
    object_template_name = SubmissionCodeView.template_name
    object_filename = 'artwork%d.pde'
    zip_filename = 'code.zip'


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

    def get_success_url(self):
        return reverse('submission-view', kwargs={'pk': self.object.id})


class DeleteSubmissionView(LoggedInMixin, ObjectHasPermMixin, SubmissionView, DeleteView):

    template_name = SubmissionView.prepend_template_path('delete.html')
    user_perm = 'can_save'
    raise_exception = True

    def get_success_url(self):
        return reverse('artwork-view', kwargs={'pk': self.object.artwork_id})
