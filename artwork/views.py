from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.core.urlresolvers import reverse
import os

from gallery.views import LoggedInMixin, ObjectHasPermMixin
from artwork.models import Artwork, ArtworkForm

from exhibitions.models import Exhibition
from submissions.models import Submission

class ArtworkView(object):
    model = Artwork
    form_class = ArtworkForm
    template_dir = 'artwork'
    save_perm = 'can_save'

    @classmethod
    def prepend_template_path(cls, *argv):
        return os.path.join(cls.template_dir, *argv)

    def get_success_url(self):
        return reverse('artwork-list')


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

            # Mark the exhibitions we've already submitted this artwork to
            for exh in exhibitions:
                exh.submitted = submissions.get(exh.id)
        
            context['submit_to_exhibitions'] = exhibitions

        return context


class ListArtworkView(ArtworkView, ListView):

    template_name = ArtworkView.prepend_template_path('list.html')


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
    user_perm = 'can_save'

    def get_error_url(self):
        return reverse('artwork-view', kwargs={'pk': self.get_object().id})

    def get_context_data(self, **kwargs):

        context = super(UpdateArtworkView, self).get_context_data(**kwargs)
        context['action'] = reverse('artwork-edit',
                                    kwargs={'pk': self.get_object().id})
        return context


class DeleteArtworkView(LoggedInMixin, ObjectHasPermMixin, ArtworkView, DeleteView):

    template_name = ArtworkView.prepend_template_path('delete.html')
    user_perm = 'can_save'

    def get_error_url(self):
        return reverse('artwork-view', kwargs={'pk': self.get_object().id})
