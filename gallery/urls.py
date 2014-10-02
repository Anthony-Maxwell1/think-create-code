from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views

import artwork.views

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    #url(r'^admin/', include(admin.site.urls)),

    url(r'^$', artwork.views.ListArtworkView.as_view(),
        name='home'),
    url(r'^$', artwork.views.ListArtworkView.as_view(),
        name='artwork-list'),
    url(r'^new/$', artwork.views.CreateArtworkView.as_view(),
        name='artwork-add'),
    url(r'^edit/(?P<pk>\d+)/$', artwork.views.UpdateArtworkView.as_view(),
        name='artwork-edit'),
    url(r'^delete/(?P<pk>\d+)/$', artwork.views.DeleteArtworkView.as_view(),
        name='artwork-delete'),
    url(r'^(?P<pk>\d+)/$', artwork.views.ShowArtworkView.as_view(),
        name='artwork-view'),
    url(r'^login/$', auth_views.login,
        {'template_name': 'login.html'},
        name='login'),
    url(r'^logout/$', auth_views.logout,
        {'next_page': '/'},
        name='logout'),
)

# n.b. Used in dev only
urlpatterns += staticfiles_urlpatterns()
