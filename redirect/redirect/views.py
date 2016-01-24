import os
import re
import json
import logging
from django.conf import settings
from django.http import JsonResponse
from django.views.generic import TemplateView, RedirectView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.urlresolvers import get_script_prefix, reverse, resolve, Resolver404, NoReverseMatch


class PathRedirectView(RedirectView):

    def get_redirect_from_path(self, path):
        # Remove our script_prefix from the path
        path = re.sub('^%s' % get_script_prefix(), '', path)

        # Append path to the redirect base
        return os.path.join(settings.REDIRECT_BASE, path)

    def get_redirect_url(self, path=None, *args, **kwargs):
        logging.debug("** PathRedirectView.get_redirect_url(path='%s'" % path)
        if not path:
            path = self.request.get_full_path()
            logging.debug('path_info: %s' % path)
        return self.get_redirect_from_path(path)


class ShareView(TemplateView):
    template_name = 'share.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ShareView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ShareView, self).get_context_data(**kwargs)
        share_path = reverse('share')
        context['post_share_url'] = self.request.build_absolute_uri(share_path)
        return context

    def post_context_data(self, **kwargs):
        path = self.request.POST.get('path')
        script_prefix = get_script_prefix()
        if not path.startswith(script_prefix):
            path = os.path.join(script_prefix, path)
        share_url = self.request.build_absolute_uri(path)
        return { 'share_url': share_url }

    def render_to_json_response(self, context, **response_kwargs):
        return JsonResponse(
            context,
            **response_kwargs
        )

    def post(self, request, *args, **kwargs):
        context = self.post_context_data(**kwargs)
        return self.render_to_json_response(context)


class WildcardRedirectView(PathRedirectView):

    def get_redirect_url(self, redirect_to, *args, **kwargs):
        path = reverse(redirect_to)
        return self.get_redirect_from_path(path)


class ObjectRedirectView(PathRedirectView):

    def __init__(self, *args, **kwargs):
        super(ObjectRedirectView, self).__init__(*args, **kwargs)
        self.model_pk_map = {}

    def get_redirect_url(self, path=None, *args, **kwargs):
        if not path:
            path = reverse('home')
        pk = self.get_pk(*args, **kwargs)
        logging.debug('** get_pk -> %s' % pk)
        if pk:
            path = self.request.path_info
            logging.debug('path_info: %s' % path)
            try:
                resolved = resolve(path)
                url_name = resolved.url_name
                url_kwargs = resolved.kwargs
                url_kwargs['pk'] = pk
                #kwargs.update(resolved.kwargs)
                #kwargs['pk'] = pk
                logging.debug('reverse(%s, kwargs=%s)' % (url_name, url_kwargs))
                path = reverse(url_name, kwargs=url_kwargs)
            except Resolver404:
                # can't resolve the URL, so just use WildcardRedirectView
                logging.debug('Resolver404')
                pass
            except NoReverseMatch:
                # can't reverse the URL, so just use WildcardRedirectView
                logging.debug('NoReverseMatch')
                pass

        # Replace current script_prefix with the redirect script_prefix
        return self.get_redirect_from_path(path)

    def get_pk(self, pk=None, model=None, *args, **kwargs):
        logging.debug('** get_pk')
        script_prefix = get_script_prefix()
        logging.debug('   script_prefix: %s' % script_prefix)
        logging.debug('   pk: %s' % pk)
        logging.debug('   model: %s' % model)
        if pk and model and (script_prefix in settings.REDIRECT_MAP):
            data_dir = settings.REDIRECT_MAP[script_prefix]
            logging.debug('   data_dir: %s' % data_dir)
        else:
            return None

        if not (script_prefix in self.model_pk_map):
            self.model_pk_map[script_prefix] = {}

        if not (model in self.model_pk_map[script_prefix]):
            try:
                data_file = os.path.join(data_dir, '%s.map.json' % model)
                fp = open(data_file)
                self.model_pk_map[script_prefix][model] = json.load(fp)
                fp.close()
            except IOError:
                # The pk map file doesn't exist, or is unreadable
                logging.debug('   IOError')
                self.model_pk_map[script_prefix][model] = {}

        return self.model_pk_map[script_prefix][model].get(pk)
