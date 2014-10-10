from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
import os

from gallery.views import LoggedInMixin
from artwork.models import Artwork, ArtworkForm

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


# TODO - consolidate these classes!
class UpdateArtworkBaseView(LoggedInMixin, ArtworkView, UpdateView):

    template_name = ArtworkView.prepend_template_path('edit.html')

    def get_context_data(self, **kwargs):

        context = super(UpdateArtworkBaseView, self).get_context_data(**kwargs)
        context['action'] = reverse('artwork-edit',
                                    kwargs={'pk': self.get_object().id})
        return context

class UpdateArtworkView(UpdateArtworkBaseView):

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.can_save(request.user):
            return super(UpdateArtworkView, self).get(request, *args, **kwargs)
        else:
            # TODO : show error message
            return HttpResponseRedirect(reverse('artwork-view', kwargs={'pk': self.object.id}))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.can_save(request.user):
            return super(UpdateArtworkView, self).post(request, *args, **kwargs)
        else:
            # TODO : show error message
            return HttpResponseRedirect(reverse('artwork-view', kwargs={'pk': self.object.id}))


class DeleteArtworkBaseView(LoggedInMixin, ArtworkView, DeleteView):

    template_name = ArtworkView.prepend_template_path('delete.html')

class DeleteArtworkView(DeleteArtworkBaseView):

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.can_save(request.user):
            return super(DeleteArtworkView, self).get(request, *args, **kwargs)
        else:
            # TODO : show error message
            return HttpResponseRedirect(reverse('artwork-view', kwargs={'pk': self.object.id}))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.can_save(request.user):
            return super(DeleteArtworkView, self).post(request, *args, **kwargs)
        else:
            # TODO : show error message
            return HttpResponseRedirect(reverse('artwork-view', kwargs={'pk': self.object.id}))

