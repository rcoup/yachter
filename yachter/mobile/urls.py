from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.simple.direct_to_template', {'template':'mobile/home.html'}),
    
    url(r'^tides/$', 'yachter.weather.views.tides'),
    url(r'^tides/heights/$', 'yachter.weather.views.tide_heights'),
    url(r'^stations/$', 'yachter.weather.views.station_list'),
    url(r'^stations/(?P<station_id>\d+)/$', 'yachter.weather.views.station_detail'),
)

