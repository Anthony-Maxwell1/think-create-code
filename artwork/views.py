from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.core.urlresolvers import reverse

from artwork.models import Artwork


class ShowArtworkView(DetailView):

    model = Artwork
    template_name = 'artwork/view.html'


class ListArtworkView(ListView):

    model = Artwork
    template_name = 'artwork/list.html'


class CreateArtworkView(CreateView):

    model = Artwork
    template_name = 'artwork/edit.html'

    def get_success_url(self):
        return reverse('artwork-list')

    def get_context_data(self, **kwargs):

        context = super(CreateArtworkView, self).get_context_data(**kwargs)
        context['action'] = reverse('artwork-add')
        return context


class UpdateArtworkView(UpdateView):

    model = Artwork
    template_name = 'artwork/edit.html'

    def get_success_url(self):
        return reverse('artwork-list')

    def get_context_data(self, **kwargs):

        context = super(UpdateArtworkView, self).get_context_data(**kwargs)
        context['action'] = reverse('artwork-edit',
                                    kwargs={'pk': self.get_object().id})
        return context


class DeleteArtworkView(DeleteView):

    model = Artwork
    template_name = 'artwork/delete.html'

    def get_success_url(self):
        return reverse('artwork-list')
