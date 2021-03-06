from django.conf import settings
from django.views.static import serve
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

from people.apps.cloud9.api import v1_public_api
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_public_api.urls)),

    url(r'^kudos/', include('apps.kudos.urls', namespace='kudos')),
    url(r'^social/', include('socialregistration.urls', namespace='socialregistration')),
    url(r'^org/', include('apps.orgchart.urls', namespace='orgchart')),
    url(r'^', include('apps.cloud9.urls', namespace='cloud9')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )