from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, TemplateView, RedirectView
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from csp.decorators import csp_update
import os

from uofa.views import TemplatePathMixin, LoggedInMixin, ObjectHasPermMixin
from artwork.models import Artwork, ArtworkForm

from exhibitions.models import Exhibition
from submissions.models import Submission

class ArtworkView(TemplatePathMixin):
    model = Artwork
    form_class = ArtworkForm
    template_dir = 'artwork'


class UnsafeMediaMixin(object):
    '''These views must be heavily protected, by HTML5 iframe attributes and parent authentication,
       to make them ok to allow inline and eval'd Javascript provided by students.
       We also disallow everything else, so that the rendered artwork can't include them.
    '''
    @method_decorator(csp_update(
        # processingjs requires *.adelaide and unsafe-eval for scripts, css, and fonts
        # (have to specify *.adelaide because of iframe security)
        SCRIPT_SRC = ("http://*.adelaide.edu.au:*", "https://*.adelaide.edu.au:*", "'unsafe-eval'",),
        STYLE_SRC =  ("http://*.adelaide.edu.au:*", "https://*.adelaide.edu.au:*",),
        FONT_SRC = ("data:",),
        # no objects, media, frames, or XHR requests allowed during render.
        # (IMG_SRC covered by default policy)
        OBJECT_SRC = ("'none'",),
        MEDIA_SRC = ("'none'",),
        FRAME_SRC = ("'none'",),
        CONNECT_SRC=("'none'",),
    ))
    def dispatch(self, *args, **kwargs):
        return super(UnsafeMediaMixin, self).dispatch(*args, **kwargs)


class ShowArtworkView(ObjectHasPermMixin, ArtworkView, DetailView):

    template_name = ArtworkView.prepend_template_path('view.html')
    user_perm = 'can_see'

    def get_context_data(self, **kwargs):
        context = super(ShowArtworkView, self).get_context_data(**kwargs)

        artwork = context['object']
        if artwork:
            # TODO : make this an AJAX query, so we can fetch on demand
            
            submissions_qs = Submission.objects.filter(
                artwork__exact=artwork.id).order_by('-created_at').all()
            submissions = { int(x.exhibition_id) : x for x in submissions_qs }

            exhibitions_qs = Exhibition.can_see_queryset(
                Exhibition.objects,
                self.request.user).order_by('-released_at')
            exhibitions = exhibitions_qs.all()

            # Collect the exhibitions we've already submitted this artwork to,
            # and the ones that can still be submitted to
            context['exhibitions_submitted'] = []
            context['exhibitions_to_submit'] = []
            for exh in exhibitions:
                submission = submissions.get(exh.id)
                if submission:
                    exh.submitted = submission
                    context['exhibitions_submitted'].append(exh)
                else:
                    context['exhibitions_to_submit'].append(exh)

        return context


class ShowArtworkCodeView(ObjectHasPermMixin, ArtworkView, DetailView):
    template_name = ArtworkView.prepend_template_path('code.pde')
    content_type = 'application/javascript; charset=utf-8'
    user_perm = 'can_see'


class RenderArtworkView(UnsafeMediaMixin, TemplateView):
    template_name = ArtworkView.prepend_template_path('render.html')

    def render_to_response(self, context, **response_kwargs):
        '''
        Ensure this page can only iframed by us.
        '''
        response = super(RenderArtworkView, self).render_to_response(context, **response_kwargs)
        response['X-Frame-Options'] = 'SAMEORIGIN';
        return response


class StudioArtworkView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        if (user.is_authenticated()):
            return reverse('artwork-author-list', kwargs={'author': user.id, 'shared': 0})
        else:
            return '%s?next=%s' % ( reverse('login'), reverse('artwork-studio') )


class ListArtworkView(ArtworkView, ListView):

    template_name = ArtworkView.prepend_template_path('list.html')
    paginate_by = 10
    paginate_orphans = 4

    def _get_author_id(self):
        return self.kwargs.get('author')

    def _get_shared(self):
        shared = self.kwargs.get('shared', None)
        if shared == '0':
            shared = False
        elif shared == None:
            shared = True
        return shared

    def get_queryset(self):
        '''Show artwork authored by the given, or current, user'''
        qs = Artwork.can_see_queryset(user=self.request.user)

        # Show a single author's work?
        author_id = self._get_author_id()
        if author_id:
            qs = qs.filter(author__exact=author_id)

        # Show shared work only?
        if self._get_shared():
            qs = qs.filter(shared__gt=0)

        # Show most recently modified first
        return qs.order_by('-modified_at')

    def get_context_data(self, **kwargs):

        context = super(ListArtworkView, self).get_context_data(**kwargs)
        user_model = get_user_model()
        author_id = self._get_author_id()
        try:
            author = user_model.objects.get(id=author_id)
        except user_model.DoesNotExist:
            author = None
        context['author'] = author

        context['shared'] = self._get_shared()
        return context


class CreateArtworkView(UnsafeMediaMixin, LoggedInMixin, ArtworkView, CreateView):

    template_name = ArtworkView.prepend_template_path('edit.html')

    def form_valid(self, form):
        # Set author to current user
        form.instance.author = self.request.user
        return super(CreateArtworkView, self).form_valid(form)

    def get_context_data(self, **kwargs):

        context = super(CreateArtworkView, self).get_context_data(**kwargs)
        context['action'] = reverse('artwork-add')
        return context


class UpdateArtworkView(UnsafeMediaMixin, LoggedInMixin, ObjectHasPermMixin, ArtworkView, UpdateView):

    template_name = ArtworkView.prepend_template_path('edit.html')
    user_perm = 'can_save'

    def get_error_url(self):
        return reverse('artwork-view', kwargs={'pk': self.get_object().id})

    def get_context_data(self, **kwargs):

        context = super(UpdateArtworkView, self).get_context_data(**kwargs)
        context['action'] = reverse('artwork-edit',
                                    kwargs={'pk': self.get_object().id})
        return context


class DeleteArtworkView(LoggedInMixin, ObjectHasPermMixin, ArtworkView, DeleteView):

    template_name = ArtworkView.prepend_template_path('delete.html')
    user_perm = 'can_save'

    def get_error_url(self):
        return reverse('artwork-view', kwargs={'pk': self.get_object().id})

    def get_success_url(self):
        return reverse('artwork-list')

