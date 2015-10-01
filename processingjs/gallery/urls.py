from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views
from django.conf import settings

import gallery.views
import artwork.views
import exhibitions.views
import submissions.views
import votes.views
import django_adelaidex.lti.views
from votes.models import Vote

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', artwork.views.ListArtworkView.as_view(),
        name='home'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^lti/', include('django_adelaidex.lti.urls')),

    # Decide whether to use auth login or django_adelaidex.lti as the 'login' url
    url(r'^login/$',
        django_adelaidex.lti.views.LTIPermissionDeniedView.as_view(),
        name='login') if settings.ADELAIDEX_LTI.get('LOGIN_URL') 
    else
    url(r'^login/$', auth_views.login,
        {'template_name': 'login.html'},
        name='login'),

    # Ensure there's always a link available for the auth login
    url(r'^auth/login/$', auth_views.login,
        {'template_name': 'login.html'},
        name='auth-login'),

    url(r'^logout/$', auth_views.logout,
        {'next_page': reverse_lazy('home')},
        name='logout'),

    # Share view
    url(r'^share/?$', gallery.views.ShareView.as_view(),
        name='share'),
    # N.B This probe.html url is used by the Nagios checks for this service.
    # PLEASE DO NOT CHANGE!
    url(r'^probe.html$', gallery.views.ProbeView.as_view(),
        name='probe'),

    # Misc static views
    url(r'^help/?$', gallery.views.HelpView.as_view(),
        name='help'),
    url(r'^terms/?$', gallery.views.TermsView.as_view(),
        name='terms'),

    # Artwork list views
    url(r'^artwork/studio/$', artwork.views.StudioArtworkView.as_view(),
        name='artwork-studio'),
    url(r'^a/?$', artwork.views.ListArtworkView.as_view(),
        {'shared': True},
        name='artwork-shared'),
    url(r'^a/list/$', artwork.views.ListArtworkView.as_view(),
        {'shared': False},
        name='artwork-list'),
    url(r'^a/by/(?P<author>\d+)/(?:(?P<shared>\d+)/)?$', artwork.views.ListArtworkView.as_view(),
        name='artwork-author-list'),

    # Zipfile Artwork list views
    url(r'^code.zip$', artwork.views.ListArtworkCodeZipFileView.as_view(),
        {'shared': True},
        name='home-zip'),
    url(r'^a/code.zip$', artwork.views.ListArtworkCodeZipFileView.as_view(),
        {'shared': True},
        name='artwork-shared-zip'),
    url(r'^a/list/code.zip$', artwork.views.ListArtworkCodeZipFileView.as_view(),
        {'shared': False},
        name='artwork-list-zip'),
    url(r'^a/by/(?P<author>\d+)/(?:(?P<shared>\d+)/)?code.zip$', artwork.views.ListArtworkCodeZipFileView.as_view(),
        name='artwork-author-list-zip'),

    # Artwork editing views
    url(r'^artwork/new/$', artwork.views.CreateArtworkView.as_view(),
        name='artwork-add'),
    url(r'^artwork/edit/(?P<pk>\d+)/$', artwork.views.UpdateArtworkView.as_view(),
        name='artwork-edit'),
    url(r'^artwork/clone/(?P<pk>\d+)/$', artwork.views.CloneArtworkView.as_view(),
        name='artwork-clone'),
    url(r'^artwork/delete/(?P<pk>\d+)/$', artwork.views.DeleteArtworkView.as_view(),
        name='artwork-delete'),

    # Artwork detail views
    url(r'^a/(?P<pk>\d+)/$', artwork.views.UpdateArtworkView.as_view(),
        name='artwork-view'),
    url(r'^artwork(?P<pk>\d+).pde$', artwork.views.ArtworkCodeView.as_view(),
        name='artwork-code'),
    url(r'^artwork/render/(?P<pk>\d+)/$', artwork.views.RenderArtworkView.as_view(),
        name='artwork-render'),
    url(r'^artwork/render/$', artwork.views.RenderArtworkView.as_view(),
        name='artwork-render-create'),

    url(r'^artwork/submit/(?P<artwork>\d+)/$', submissions.views.CreateSubmissionView.as_view(),
        name='artwork-submit'),

    # Exhibition views
    url(r'^e/?$', exhibitions.views.ListExhibitionView.as_view(),
        name='exhibition-list'),
    url(r'^e/(?P<pk>\d+)/score/$', exhibitions.views.ShowExhibitionView.as_view(),
        {'order': 'score'},
        name='exhibition-view-score'),
    url(r'^e/list/(?P<pk_list>[\d,]+)?/?$', exhibitions.views.ListExhibitionView.as_view(),
        {'separator': ','},
        name='exhibition-list'),
    url(r'^e/(?P<pk>\d+)/$', exhibitions.views.ShowExhibitionView.as_view(),
        {'order': 'recent'},
        name='exhibition-view'),
    url(r'^exhibition/new/$', exhibitions.views.CreateExhibitionView.as_view(),
        name='exhibition-add'),
    url(r'^exhibition/edit/(?P<pk>\d+)/$', exhibitions.views.UpdateExhibitionView.as_view(),
        name='exhibition-edit'),
    url(r'^exhibition/delete/(?P<pk>\d+)/$', exhibitions.views.DeleteExhibitionView.as_view(),
        name='exhibition-delete'),

    # Submission views
    url(r'^s/(?P<pk>\d+)/$', submissions.views.ShowSubmissionView.as_view(),
        name='submission-view'),
    url(r'^submission/delete/(?P<pk>\d+)/$', submissions.views.DeleteSubmissionView.as_view(),
        name='submission-delete'),
    url(r'^submission/like/(?P<submission>\d+)/$', votes.views.CreateVoteView.as_view(), {'status': Vote.THUMBS_UP},
        name='submission-like'),
    url(r'^submission/unlike/(?P<submission>\d+)/$', votes.views.DeleteVoteView.as_view(),
        name='submission-unlike'),

    # Vote views
    url(r'^vote/ok/$', votes.views.NoOpView.as_view(),
        name='vote-ok'),
    url(r'^vote/(?P<pk>\d+)$', votes.views.ShowVoteView.as_view(),
        name='vote-view'),

    url(r'^media/(?P<name>.+)$', 'database_files.views.serve',
        name='database_file'),
)

# n.b. Used in dev only
urlpatterns += staticfiles_urlpatterns()
