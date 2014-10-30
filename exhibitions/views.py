import os
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse

from gallery.views import LoggedInMixin, ObjectHasPermMixin, ModelHasPermMixin
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

    def get_error_url(self):
        return reverse('exhibition-list')

    def get_model(self):
        return self.model

    def get_context_data(self, **kwargs):
        context = super(ExhibitionView, self).get_context_data(**kwargs)
        context['model'] = self.get_model()
        return context


class ListExhibitionView(ExhibitionView, ListView):

    template_name = ExhibitionView.prepend_template_path('list.html')

    def get_queryset(self):
        '''Enforce model queryset restrictions, and sort by released_at desc'''
        qs = super(ExhibitionView, self).get_queryset()
        qs = self.get_model().can_see_queryset(qs, self.request.user)
        return qs.order_by('-released_at')


class ShowExhibitionView(ObjectHasPermMixin, ExhibitionView, DetailView):

    template_name = ExhibitionView.prepend_template_path('view.html')
    user_perm = 'can_see'
    raise_exception = True


class CreateExhibitionView(LoggedInMixin, ModelHasPermMixin, ExhibitionView, CreateView):

    template_name = ExhibitionView.prepend_template_path('edit.html')
    user_perm = 'can_save'

    def form_valid(self, form):
        # Set author to current user
        form.instance.author = self.request.user
        return super(CreateExhibitionView, self).form_valid(form)

    def get_context_data(self, **kwargs):

        context = super(CreateExhibitionView, self).get_context_data(**kwargs)
        context['action'] = reverse('exhibition-add')
        return context


class UpdateExhibitionView(LoggedInMixin, ModelHasPermMixin, ExhibitionView, UpdateView):

    template_name = ExhibitionView.prepend_template_path('edit.html')
    user_perm = 'can_save'

    def get_context_data(self, **kwargs):

        context = super(UpdateExhibitionView, self).get_context_data(**kwargs)
        context['action'] = reverse('exhibition-edit',
                                    kwargs={'pk': self.get_object().id})
        return context


class DeleteExhibitionView(LoggedInMixin, ModelHasPermMixin, ExhibitionView, DeleteView):

    template_name = ExhibitionView.prepend_template_path('delete.html')
    user_perm = 'can_save'

    def get_success_url(self):
        return self.get_error_url()
