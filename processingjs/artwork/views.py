from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
import os

from uofa.views import TemplatePathMixin, LoggedInMixin, ObjectHasPermMixin
from artwork.models import Artwork, ArtworkForm

from exhibitions.models import Exhibition
from submissions.models import Submission

class ArtworkView(TemplatePathMixin):
    model = Artwork
    form_class = ArtworkForm
    template_dir = 'artwork'


class ShowArtworkView(ArtworkView, DetailView):

    template_name = ArtworkView.prepend_template_path('view.html')

    def get_context_data(self, **kwargs):
        context = super(ShowArtworkView, self).get_context_data(**kwargs)

        artwork = context['object']
        if artwork:
            # TODO : make this an AJAX query, so we can fetch on demand
            
            submissions_qs = Submission.objects.filter(
                artwork__exact=artwork.id).order_by('-created_at').all()
            submissions = { int(x.exhibition_id) : x for x in submissions_qs }

            exhibitions_qs = Exhibition.can_see_queryset(
                Exhibition.objects,
                self.request.user).order_by('-released_at')
            exhibitions = exhibitions_qs.all()

            # Collect the exhibitions we've already submitted this artwork to,
            # and the ones that can still be submitted to
            context['exhibitions_submitted'] = []
            context['exhibitions_to_submit'] = []
            for exh in exhibitions:
                submission = submissions.get(exh.id)
                if submission:
                    exh.submitted = submission
                    context['exhibitions_submitted'].append(exh)
                else:
                    context['exhibitions_to_submit'].append(exh)

        return context


class ShowArtworkCodeView(ArtworkView, DetailView):
    template_name = ArtworkView.prepend_template_path('code.pde')
    content_type = 'application/javascript; charset=utf-8'


class RenderArtworkView(ArtworkView, DetailView):
    template_name = ArtworkView.prepend_template_path('render.html')


class ListArtworkView(ArtworkView, ListView):

    template_name = ArtworkView.prepend_template_path('list.html')

    def _get_author_id(self):
        author_id = self.kwargs.get('author')
        if not author_id and self.request.user.is_authenticated():
            author_id = self.request.user.id
        return author_id

    def get_queryset(self):
        '''Show artwork authored by the given, or current, user'''
        qs = super(ListArtworkView, self).get_queryset()
        author_id = self._get_author_id()
        if author_id:
            qs = qs.filter(author__exact=author_id).order_by('-modified_at')
        return qs

    def get_context_data(self, **kwargs):

        context = super(ListArtworkView, self).get_context_data(**kwargs)
        user_model = get_user_model()
        author_id = self._get_author_id()
        try:
            author = user_model.objects.get(id=author_id)
        except user_model.DoesNotExist:
            author = None
        context['author'] = author
        return context


class CreateArtworkView(LoggedInMixin, ArtworkView, CreateView):

    template_name = ArtworkView.prepend_template_path('edit.html')

    def form_valid(self, form):
        # Set author to current user
        form.instance.author = self.request.user
        return super(CreateArtworkView, self).form_valid(form)

    def get_context_data(self, **kwargs):

        context = super(CreateArtworkView, self).get_context_data(**kwargs)
        context['action'] = reverse('artwork-add')
        return context


class UpdateArtworkView(LoggedInMixin, ObjectHasPermMixin, ArtworkView, UpdateView):

    template_name = ArtworkView.prepend_template_path('edit.html')
    user_perm = 'can_edit'

    def get_error_url(self):
        return reverse('artwork-view', kwargs={'pk': self.get_object().id})

    def get_context_data(self, **kwargs):

        context = super(UpdateArtworkView, self).get_context_data(**kwargs)
        context['action'] = reverse('artwork-edit',
                                    kwargs={'pk': self.get_object().id})
        return context


class DeleteArtworkView(LoggedInMixin, ObjectHasPermMixin, ArtworkView, DeleteView):

    template_name = ArtworkView.prepend_template_path('delete.html')
    user_perm = 'can_delete'

    def get_error_url(self):
        return reverse('artwork-view', kwargs={'pk': self.get_object().id})

    def get_success_url(self):
        return reverse('artwork-list')

