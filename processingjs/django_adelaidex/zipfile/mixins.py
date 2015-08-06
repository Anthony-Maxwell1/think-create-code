'''
Mixin for use with django.views.generic.ListView or DetailView, which renders object(s)
to individual files in a downloadable zip file.

Usage:

# List view
from django.views.generic.ListView
from myapp.models import Model
class ZipFileListView(ZipFileViewMixin, ListView):
    object_template_name = 'view.html' # required
    object_filename = 'obj%d.html'
    zip_filename = 'list.zip'
    model = Model

# Detail view
from django.views.generic.DetailView
from myapp.models import Model
class ZipFileDetailView(ZipFileViewMixin, DetailView):
    object_template_name = 'view.html' # required
    model = Model

'''
from django.template import RequestContext
from django.template.loader import render_to_string

from django_adelaidex.zipfile.response import ZipFileResponse


class ZipFileViewMixin(object):

    # must be set in subclass
    object_template_name = None

    # override in subclass
    object_filename = 'obj%d'
    zip_filename = 'download.zip'

    # override at your peril
    response_class = ZipFileResponse
    object_template_dirs = None

    def __init__(self, *args, **kwargs):
        if not self.object_template_name:
            raise UnboundLocalError('%s.object_template_name' % self.__class__.__name__)
        super(ZipFileViewMixin, self).__init__(*args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        response = self.response_class(filename=self.zip_filename, **response_kwargs)
        objects = context.get('object_list', [])
        if not objects and 'object' in context and context['object']:
            objects = [context['object']]

        # Create a single object context to render
        for obj in objects:
            obj_context = RequestContext(self.request, context)
            obj_context.update({
                'object': obj, 
                'object_list': None,
                obj._meta.model_name: obj, 
                self.get_context_object_name(objects): None})

            filename = self.object_filename % obj.pk
            rendered = render_to_string(
                template_name=self.object_template_name,
                context_instance=obj_context,
                dirs=self.object_template_dirs,
            )
            response.append(filename, rendered)

        response.close()
        return response
