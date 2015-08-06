import os.path
import re
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse, get_script_prefix
from django.conf import settings
from django_adelaidex.mixins import TemplatePathMixin


class ProbeView(TemplatePathMixin, TemplateView):
    TemplatePathMixin.template_dir = 'gallery'
    template_name = TemplatePathMixin.prepend_template_path('probe.html')


class HelpView(TemplatePathMixin, TemplateView):
    TemplatePathMixin.template_dir = 'gallery'
    template_name = TemplatePathMixin.prepend_template_path('help.html')


class TermsView(TemplatePathMixin, TemplateView):
    TemplatePathMixin.template_dir = 'gallery'
    template_name = TemplatePathMixin.prepend_template_path('terms.html')


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
