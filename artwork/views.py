from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.core.urlresolvers import reverse
import os

from artwork.models import Artwork, ArtworkForm

class ArtworkView:
    model = Artwork
    form_class = ArtworkForm
    template_dir = 'artwork'

    @classmethod
    def prepend_template_path(cls, *argv):
        return os.path.join(cls.template_dir, *argv)

    def get_success_url(self):
        return reverse('artwork-list')


class ShowArtworkView(ArtworkView, DetailView):

    template_name = ArtworkView.prepend_template_path('view.html')


class ListArtworkView(ArtworkView, ListView):

    template_name = ArtworkView.prepend_template_path('list.html')


class CreateArtworkView(ArtworkView, CreateView):

    template_name = ArtworkView.prepend_template_path('edit.html')

    def get_context_data(self, **kwargs):

        context = super(CreateArtworkView, self).get_context_data(**kwargs)
        context['action'] = reverse('artwork-add')
        return context


class UpdateArtworkView(ArtworkView, UpdateView):

    template_name = ArtworkView.prepend_template_path('edit.html')

    def get_context_data(self, **kwargs):

        context = super(UpdateArtworkView, self).get_context_data(**kwargs)
        context['action'] = reverse('artwork-edit',
                                    kwargs={'pk': self.get_object().id})
        return context


class DeleteArtworkView(ArtworkView, DeleteView):

    template_name = ArtworkView.prepend_template_path('delete.html')
