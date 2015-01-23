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
    url(r'^help/$', gallery.views.HelpView.as_view(),
        name='help'),
    url(r'^artwork/studio/$', artwork.views.StudioArtworkView.as_view(),
        name='artwork-studio'),
    url(r'^artwork/shared/$', artwork.views.ListArtworkView.as_view(),
        {'shared': True},
        name='artwork-shared'),
    url(r'^artwork/list/$', artwork.views.ListArtworkView.as_view(),
        {'shared': False},
        name='artwork-list'),
    url(r'^artwork/list/(?P<author>\d+)/(?:(?P<shared>\d+)/)?$', artwork.views.ListArtworkView.as_view(),
        name='artwork-author-list'),
    url(r'^artwork/new/$', artwork.views.CreateArtworkView.as_view(),
        name='artwork-add'),
    url(r'^artwork/edit/(?P<pk>\d+)/$', artwork.views.UpdateArtworkView.as_view(),
        name='artwork-edit'),
    url(r'^artwork/delete/(?P<pk>\d+)/$', artwork.views.DeleteArtworkView.as_view(),
        name='artwork-delete'),
    url(r'^artwork/(?P<pk>\d+)/$', artwork.views.ShowArtworkView.as_view(),
        name='artwork-view'),
    url(r'^artwork/(?P<pk>\d+)/code.pde$', artwork.views.ShowArtworkCodeView.as_view(),
        name='artwork-code'),
    url(r'^artwork/render/(?P<pk>\d+)/$', artwork.views.RenderArtworkView.as_view(),
        name='artwork-render'),
    url(r'^artwork/submit/(?P<artwork>\d+)/$', submissions.views.CreateSubmissionView.as_view(),
        name='artwork-submit'),
    url(r'^exhibitions/?$', exhibitions.views.ListExhibitionView.as_view(),
        name='exhibition-list'),
    url(r'^exhibitions/(?P<pk>\d+)/$', exhibitions.views.ShowExhibitionView.as_view(),
        name='exhibition-view'),
    url(r'^exhibitions/new/$', exhibitions.views.CreateExhibitionView.as_view(),
        name='exhibition-add'),
    url(r'^exhibitions/edit/(?P<pk>\d+)/$', exhibitions.views.UpdateExhibitionView.as_view(),
        name='exhibition-edit'),
    url(r'^exhibitions/delete/(?P<pk>\d+)/$', exhibitions.views.DeleteExhibitionView.as_view(),
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
        name='logout'),
    url(r'^media/(?P<name>.+)$', 'database_files.views.serve',
        name='database_file'),
)

# n.b. Used in dev only
urlpatterns += staticfiles_urlpatterns()
