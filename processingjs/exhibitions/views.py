import os
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from csp.decorators import csp_update

from django_adelaidex.util.mixins import TemplatePathMixin, LoggedInMixin, ObjectHasPermMixin, ModelHasPermMixin
from gallery.views import ShareView
from exhibitions.models import Exhibition, ExhibitionForm

from submissions.views import ListSubmissionView


class ExhibitionView(TemplatePathMixin):
    model = Exhibition
    form_class = ExhibitionForm
    template_dir = 'exhibitions'

    def get_success_url(self):
        return reverse('exhibition-view', kwargs={'pk': self.object.id})

    def get_error_url(self):
        return reverse('exhibition-list')

    def get_model(self):
        return self.model

    def get_context_data(self, **kwargs):
        context = super(ExhibitionView, self).get_context_data(**kwargs)
        context['model'] = self.get_model()

        exhibition = context.get('object')
        if exhibition:
            context['share_url'] = ShareView.reverse_share_url(
                'exhibition-view',
                kwargs={'pk': exhibition.id})

        return context


class ListExhibitionView(ExhibitionView, ListView):

    template_name = ExhibitionView.prepend_template_path('list.html')

    def get_queryset(self):
        '''Enforce model queryset restrictions, and sort by released_at desc'''
        qs = super(ExhibitionView, self).get_queryset()
        qs = self.get_model().can_see_queryset(qs, self.request.user)
        return qs.order_by('-released_at', 'created_at')


class ShowExhibitionView(ObjectHasPermMixin, ExhibitionView, DetailView):

    template_name = ExhibitionView.prepend_template_path('view.html')
    user_perm = 'can_see'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(ShowExhibitionView, self).get_context_data(**kwargs)

        # Paginate the submission_set using our kwargs
        submissions_list_view = ListSubmissionView()
        submissions_list_view.request = self.request
        submissions_list_view.args = self.args
        submissions_list_view.kwargs = self.kwargs
        submissions_list_view.object_list = submissions_list_view.get_queryset()
        context['submissions'] = submissions_list_view.get_context_data()

        return context

class UnsafeJSEvalMixin(object):
    @method_decorator(csp_update(
        # jquery.datetimepicker.min.js requires javascript eval
        SCRIPT_SRC = ("'unsafe-eval'",),
    ))
    def dispatch(self, *args, **kwargs):
        return super(UnsafeJSEvalMixin, self).dispatch(*args, **kwargs)

class CreateExhibitionView(UnsafeJSEvalMixin, LoggedInMixin, ModelHasPermMixin, ExhibitionView, CreateView):

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


class UpdateExhibitionView(UnsafeJSEvalMixin, LoggedInMixin, ModelHasPermMixin, ExhibitionView, UpdateView):

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
