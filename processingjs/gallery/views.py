import os.path
from django.views.generic import UpdateView
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse, resolve
from django.utils.http import is_safe_url
from django.conf import settings
from django.http import HttpResponseRedirect
from harvard.django_auth_lti.mixins import LTIUtilityMixin, LTIRoleRestrictionMixin
from uofa.models import UserForm
from uofa.views import TemplatePathMixin, CSRFExemptMixin

import logging
logger = logging.getLogger(__name__)


class LTILoginView(CSRFExemptMixin, LTIUtilityMixin, TemplatePathMixin, UpdateView):

    form_class = UserForm
    model = UserForm._meta.model

    TemplatePathMixin.template_dir = 'gallery'
    template_name = TemplatePathMixin.prepend_template_path('lti.html')

    def post(self, request, *args, **kwargs):

        # If we already have a first_name, skip this form.
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        obj = self.get_object()
        if obj.first_name:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)

    def get_object(self):
        return get_object_or_404(self.model, pk=self.request.user.id)

    def get_success_url(self):

        url_name = 'home'
        custom_page = self.request.POST.get('custom_page')
        if custom_page and is_safe_url(url=custom_page, host=self.request.get_host()):
            url_name = resolve(custom_page).url_name

        return reverse(url_name)
