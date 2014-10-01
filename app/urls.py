from django.conf.urls import patterns, include, url
# FIXME - dev only
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

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
)

# FIXME - dev only
urlpatterns += staticfiles_urlpatterns()
