import os.path
import re
from django.views.generic import UpdateView, TemplateView, RedirectView
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse, resolve, get_script_prefix
from django.http import HttpResponse
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.http import is_safe_url
from django.conf import settings
from django.http import HttpResponseRedirect
from django_auth_lti.mixins import LTIUtilityMixin, LTIRoleRestrictionMixin
import pickle

from uofa.models import UserForm
from uofa.views import TemplatePathMixin, CSRFExemptMixin
import gallery.settings


class ProbeView(TemplatePathMixin, TemplateView):
    TemplatePathMixin.template_dir = 'gallery'
    template_name = TemplatePathMixin.prepend_template_path('probe.html')


class HelpView(TemplatePathMixin, TemplateView):
    TemplatePathMixin.template_dir = 'gallery'
    template_name = TemplatePathMixin.prepend_template_path('help.html')


class ShareView(TemplatePathMixin, TemplateView):
    TemplatePathMixin.template_dir = 'gallery'
    template_name = TemplatePathMixin.prepend_template_path('share.html')

    @classmethod
    def get_share_url(cls, url=None):
        '''Returns an absolute URL suitable for sharing the given view'''
        share_url = settings.SHARE_URL
        if url:
            # Strip leading script prefix, trailing /
            url = re.sub(r'^%s' % get_script_prefix(), '', url)
            url = re.sub(r'/$', '', url)
            share_url = '%s?#%s' % (share_url, url)
        return share_url

    @classmethod
    def reverse_share_url(cls, view=None, *args, **kwargs):
        '''Reverses a URL suitable for sharing the given view'''
        url = None
        if view:
            url = reverse(view, *args, **kwargs)
        return cls.get_share_url(url)

    def get_context_data(self, **kwargs):
        context = super(ShareView, self).get_context_data(**kwargs)
        context['script_prefix'] = get_script_prefix()
        return context


class LTIPermissionDeniedView(TemplatePathMixin, TemplateView):

    TemplatePathMixin.template_dir = 'gallery'
    template_name = TemplatePathMixin.prepend_template_path('lti-403.html')

    def get_context_data(self, **kwargs):
        context = super(LTIPermissionDeniedView, self).get_context_data(**kwargs)
        context['lti_link_text'] = gallery.settings.LTI_LINK_TEXT
        context['lti_query_string'] = self.request.META.get('QUERY_STRING', '')
        if context['lti_query_string']:
            context['lti_query_string'] = '?' + context['lti_query_string']
        return context


class LTIRedirectView(RedirectView):

    # Send 302, in case we need to change anything
    permanent=False

    # Store current GET parms to a cookie, to be used by LTIEntryView.get_success_url()
    def dispatch(self, *args, **kwargs):

        if 'redirect_url' in kwargs:
            self.redirect_url = kwargs['redirect_url']
            del kwargs['redirect_url']

        response = super(LTIRedirectView, self).dispatch(*args, **kwargs)

        # Store the given persistent parameters, serialized, in a cookie
        store_params = {}
        for key in gallery.settings.LTI_PERSIST_PARAMS:
            store_params[key] = self.request.GET.get(key)
        try:
            store_params = pickle.dumps(store_params)
            response.set_cookie(gallery.settings.LTI_PERSIST_NAME, store_params)
        except:
            pass # ignore corrupted params or other pickling errors

        return response

    def get_redirect_url(self):
        return self.redirect_url


class LTIEntryView(CSRFExemptMixin, LTIUtilityMixin, TemplatePathMixin, UpdateView):

    form_class = UserForm
    model = UserForm._meta.model

    TemplatePathMixin.template_dir = 'gallery'
    template_name = TemplatePathMixin.prepend_template_path('lti-entry.html')

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return super(LTIEntryView, self).get(request, *args, **kwargs)
        return HttpResponseRedirect('%s?next=%s' % (reverse('login'), self.request.get_full_path()))

    def post(self, request, *args, **kwargs):
        '''Bypass this form if we already have a user.first_name 
           (and we're not trying to POST an update).'''

        self.object = self.get_object()
        if not 'first_name' in self.request.POST and self.object.first_name:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super(LTIEntryView, self).post(request, *args, **kwargs)

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

        response = super(LTIEntryView, self).form_valid(form)

        # clear out the persistent LTI parameters; 
        # they've been used by get_success_url()
        #FIXME response.set_cookie(gallery.settings.LTI_PERSIST_NAME, '')
        response.delete_cookie(gallery.settings.LTI_PERSIST_NAME)

        return response

    def get_success_url(self):
        '''If LTIRedirectView or edX sent a 'next' query parameter, redirect there.
           Otherwise, redirect to home.'''

        url_name = 'home'
        kwargs = {}
        next_param = None

        # See if this request started from an LTIRedirectView, and so has a cookie.
        cookie = self.request.COOKIES.get(gallery.settings.LTI_PERSIST_NAME)
        if cookie:
            try:
                stored_params = pickle.loads(cookie)
                next_param = stored_params.get(REDIRECT_FIELD_NAME)
            except:
                pass # ignore corrupted cookies or errors during unpickling

        # If no next param found in cookie, get it from the POST request
        if not next_param:
            next_param = self.request.POST.get('custom_next')

        if next_param and is_safe_url(url=next_param, host=self.request.get_host()):
            resolved = resolve(next_param)
            url_name = resolved.url_name
            kwargs = resolved.kwargs

        return reverse(url_name, kwargs=kwargs)
