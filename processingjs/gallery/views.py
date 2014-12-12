import os.path
from django.views.generic import UpdateView
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse, resolve
from django.utils.http import is_safe_url
from django.conf import settings
from django.http import HttpResponseRedirect
from django_auth_lti.mixins import LTIUtilityMixin, LTIRoleRestrictionMixin
from uofa.models import UserForm
from uofa.views import TemplatePathMixin, CSRFExemptMixin


class LTILoginView(CSRFExemptMixin, LTIUtilityMixin, TemplatePathMixin, UpdateView):

    form_class = UserForm
    model = UserForm._meta.model

    TemplatePathMixin.template_dir = 'gallery'
    template_name = TemplatePathMixin.prepend_template_path('lti-login.html')

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(LTILoginView, self).get(request, *args, **kwargs)
        return HttpResponseRedirect('%s?next=%s' % (reverse('login'), self.request.get_full_path()))

    def post(self, request, *args, **kwargs):
        '''Bypass this form if we already have a user.first_name 
           (and we're not trying to POST an update).'''

        self.object = self.get_object()
        if not 'first_name' in self.request.POST and self.object.first_name:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(LTILoginView, self).post(request, *args, **kwargs)

    def get_object(self):
        '''This view's object is the current user'''
        return get_object_or_404(self.model, pk=self.request.user.id)

    def form_valid(self, form):
        '''Set is_staff setting based on LTI User roles'''

        roles = self.current_user_roles()
        if 'Instructor' in roles:
            form.instance.is_staff = True
        else:
            form.instance.is_staff = False

        return super(LTILoginView, self).form_valid(form)

    def get_success_url(self):
        '''If edX sent a 'next' query parameter, redirect there.
           Otherwise, redirect to home.'''

        url_name = 'home'
        kwargs = {}
        custom_next = self.request.POST.get('custom_next')
        if custom_next and is_safe_url(url=custom_next, host=self.request.get_host()):
            resolved = resolve(custom_next)
            url_name = resolved.url_name
            kwargs = resolved.kwargs

        return reverse(url_name, kwargs=kwargs)