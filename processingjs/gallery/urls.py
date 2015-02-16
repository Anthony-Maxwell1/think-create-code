from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views

import gallery.views
import artwork.views
import exhibitions.views
import submissions.views
import votes.views
from votes.models import Vote

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    #url(r'^admin/', include(admin.site.urls)),

    url(r'^$', artwork.views.ListArtworkView.as_view(),
        name='home'),
    url(r'^lti/$', gallery.views.LTILoginView.as_view(),
        name='lti-login'),
    url(r'^share/?$', gallery.views.ShareView.as_view(),
        name='share'),
    # N.B This /help url is used by the Nagios checks for this service.
    # PLEAE DO NOT CHANGE!
    url(r'^probe.html$', gallery.views.ProbeView.as_view(),
        name='probe'),
    url(r'^help/?$', gallery.views.HelpView.as_view(),
        name='help'),
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
    url(r'^artwork/new/$', artwork.views.CreateArtworkView.as_view(),
        name='artwork-add'),
    url(r'^artwork/edit/(?P<pk>\d+)/$', artwork.views.UpdateArtworkView.as_view(),
        name='artwork-edit'),
    url(r'^artwork/delete/(?P<pk>\d+)/$', artwork.views.DeleteArtworkView.as_view(),
        name='artwork-delete'),
    url(r'^a/(?P<pk>\d+)/$', artwork.views.UpdateArtworkView.as_view(),
        name='artwork-view'),
    url(r'^artwork/render/(?P<pk>\d+)/$', artwork.views.RenderArtworkView.as_view(),
        name='artwork-render'),
    url(r'^artwork/render/$', artwork.views.RenderArtworkView.as_view(),
        name='artwork-render-create'),
    url(r'^artwork/submit/(?P<artwork>\d+)/$', submissions.views.CreateSubmissionView.as_view(),
        name='artwork-submit'),
    url(r'^e/?$', exhibitions.views.ListExhibitionView.as_view(),
        name='exhibition-list'),
    url(r'^e/(?P<pk>\d+)/score/$', exhibitions.views.ShowExhibitionView.as_view(),
        {'order': 'score'},
        name='exhibition-view-score'),
    url(r'^e/(?P<pk>\d+)/$', exhibitions.views.ShowExhibitionView.as_view(),
        {'order': 'recent'},
        name='exhibition-view'),
    url(r'^exhibition/new/$', exhibitions.views.CreateExhibitionView.as_view(),
        name='exhibition-add'),
    url(r'^exhibition/edit/(?P<pk>\d+)/$', exhibitions.views.UpdateExhibitionView.as_view(),
        name='exhibition-edit'),
    url(r'^exhibition/delete/(?P<pk>\d+)/$', exhibitions.views.DeleteExhibitionView.as_view(),
        name='exhibition-delete'),
    url(r'^submission/delete/(?P<pk>\d+)/$', submissions.views.DeleteSubmissionView.as_view(),
        name='submission-delete'),
    url(r'^submission/like/(?P<submission>\d+)/$', votes.views.CreateVoteView.as_view(), {'status': Vote.THUMBS_UP},
        name='submission-like'),
    url(r'^submission/unlike/(?P<submission>\d+)/$', votes.views.DeleteVoteView.as_view(),
        name='submission-unlike'),
    url(r'^vote/ok/$', votes.views.NoOpView.as_view(),
        name='vote-ok'),
    url(r'^vote/(?P<pk>\d+)$', votes.views.ShowVoteView.as_view(),
        name='vote-view'),
    url(r'^login/$', auth_views.login,
        {'template_name': 'login.html'},
        name='login'),
    url(r'^logout/$', auth_views.logout,
        {'next_page': '/'},
        name='logout'),
    url(r'^media/(?P<name>.+)$', 'database_files.views.serve',
        name='database_file'),
)

# n.b. Used in dev only
urlpatterns += staticfiles_urlpatterns()
