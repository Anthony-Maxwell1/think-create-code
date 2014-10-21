import os
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse

from gallery.views import LoggedInMixin
from exhibitions.models import Exhibition, ExhibitionForm

class ExhibitionView(object):
    model = Exhibition
    form_class = ExhibitionForm
    template_dir = 'exhibitions'

    @classmethod
    def prepend_template_path(cls, *argv):
        return os.path.join(cls.template_dir, *argv)

    def get_success_url(self):
        return reverse('exhibition-view', kwargs={'pk': self.object.id})


class ListExhibitionView(ExhibitionView, ListView):

    template_name = ExhibitionView.prepend_template_path('list.html')


class ShowExhibitionView(ExhibitionView, DetailView):

    template_name = ExhibitionView.prepend_template_path('view.html')


class CreateExhibitionView(LoggedInMixin, ExhibitionView, CreateView):

    template_name = ExhibitionView.prepend_template_path('edit.html')

    def form_valid(self, form):
        # Set author to current user
        form.instance.author = self.request.user
        return super(CreateExhibitionView, self).form_valid(form)

    def get_context_data(self, **kwargs):

        context = super(CreateExhibitionView, self).get_context_data(**kwargs)
        context['action'] = reverse('exhibition-add')
        return context


class UpdateExhibitionView(LoggedInMixin, ExhibitionView, UpdateView):

    template_name = ExhibitionView.prepend_template_path('edit.html')

    def get_context_data(self, **kwargs):

        context = super(UpdateExhibitionView, self).get_context_data(**kwargs)
        context['action'] = reverse('exhibition-edit',
                                    kwargs={'pk': self.get_object().id})
        return context


class DeleteExhibitionView(LoggedInMixin, ExhibitionView, DeleteView):

    template_name = ExhibitionView.prepend_template_path('delete.html')

    def get_success_url(self):
        return reverse('exhibition-list')

