from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, TemplateView, RedirectView
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from csp.decorators import csp_replace
from django.core.exceptions import PermissionDenied
import os

from uofa.views import TemplatePathMixin, LoggedInMixin, ObjectHasPermMixin, MethodObjectHasPermMixin
from gallery.views import ShareView
from artwork.models import Artwork, ArtworkForm

from exhibitions.models import Exhibition
from submissions.models import Submission
from votes.models import Vote

class ArtworkView(TemplatePathMixin):
    model = Artwork
    form_class = ArtworkForm
    template_dir = 'artwork'


class RenderArtworkView(TemplateView):
    template_name = ArtworkView.prepend_template_path('render.html')

    '''This view must be heavily protected, by HTML5 iframe attributes and parent authentication,
       to make them ok to allow inline and eval'd Javascript provided by students.
       We also disallow everything else, so that the rendered artwork can't include them.
    '''
    @method_decorator(csp_replace(
        # processingjs requires *.adelaide and unsafe-eval for scripts, css, and fonts
        # (have to specify *.adelaide because of iframe security)
        SCRIPT_SRC = ("http://*.adelaide.edu.au:*", "https://*.adelaide.edu.au:*", "'unsafe-eval'",),
        STYLE_SRC =  ("http://*.adelaide.edu.au:*", "https://*.adelaide.edu.au:*", "'unsafe-inline'", ),
        FONT_SRC = ("'self'", "data:",),
        # no objects, media, frames, or XHR requests allowed during render.
        # (IMG_SRC covered by default policy)
        OBJECT_SRC = ("'none'",),
        MEDIA_SRC = ("'none'",),
        FRAME_SRC = ("'none'",),
        CONNECT_SRC=("'none'",),
    ))
    def dispatch(self, *args, **kwargs):
        return super(RenderArtworkView, self).dispatch(*args, **kwargs)


class StudioArtworkView(LoggedInMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        return reverse('artwork-author-list', kwargs={'author': user.id, 'shared': 0})


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

        # Fetch submissions for these artworks
        artwork_ids = [ a.id for a in context['object_list']]
        submissions = Submission.objects.filter(artwork__id__in=artwork_ids).all()
        context['submissions'] = { s.artwork_id:s for s in submissions }

        # Fetch votes for these submissions
        submission_ids = [ s.id for s in submissions ]
        votes = Vote.can_delete_queryset(user=self.request.user, submission=submission_ids).all()
        context['votes'] = { v.submission_id:v for v in votes }

        context['disqus_shortname'] = settings.DISQUS_SHORTNAME

        return context


class CreateArtworkView(LoggedInMixin, ArtworkView, CreateView):

    template_name = ArtworkView.prepend_template_path('edit.html')

    def form_valid(self, form):
        # Set author to current user
        form.instance.author = self.request.user
        return super(CreateArtworkView, self).form_valid(form)

    def get_context_data(self, **kwargs):

        context = super(CreateArtworkView, self).get_context_data(**kwargs)
        context['action'] = reverse('artwork-add')
        context['USER_CAN_SAVE'] = True
        return context


class CloneArtworkView(CreateArtworkView):
    '''Create a new Artwork, cloned from an existing artwork'''

    clone_title = '[Clone] {title}'
    clone_code = "/* Cloned from {url} */\n{code}"

    def get_initial(self):
        self.cloned = self.get_object()
        return {
            'title': self.clone_title.format(title=self.cloned.title),
            'code': self.clone_code.format(
                code=self.cloned.code,
                url=self.request.build_absolute_uri(
                    reverse('artwork-view', kwargs={'pk': self.cloned.id}))
            ),
        }

    def get(self, request, *args, **kwargs):
        return super(CloneArtworkView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CloneArtworkView, self).get_context_data(**kwargs)
        context['cloned'] = self.cloned
        return context


class UpdateArtworkView(MethodObjectHasPermMixin, ArtworkView, UpdateView):

    template_name = ArtworkView.prepend_template_path('edit.html')
    method_user_perm = { 'GET': 'can_see', 'POST': 'can_save' }

    def get_context_data(self, **kwargs):

        context = super(UpdateArtworkView, self).get_context_data(**kwargs)
        context['action'] = reverse('artwork-edit',
                                    kwargs={'pk': self.get_object().id})

        artwork = context['object']
        if artwork:
            context['share_url'] = ShareView.get_share_url(artwork.get_absolute_url())

            submissions_qs = Submission.objects.filter(
                artwork__exact=artwork.id).order_by('-created_at').all()
            submissions = { int(x.exhibition_id) : x for x in submissions_qs }

            exhibitions_qs = Exhibition.can_see_queryset(
                Exhibition.objects,
                self.request.user).order_by('-released_at', 'created_at')
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


class DeleteArtworkView(LoggedInMixin, ObjectHasPermMixin, ArtworkView, DeleteView):

    template_name = ArtworkView.prepend_template_path('delete.html')
    user_perm = 'can_save'

    def get_error_url(self):
        return self.get_object().get_absolute_url()

    def get_success_url(self):
        return reverse('artwork-list')
