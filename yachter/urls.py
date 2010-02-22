from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    #url(r'^courses/course/(?P<course_id>\d+)/map/$', 'yachter.courses.views.course', name='course-map'),
    #url(r'^courses/course/map/$', 'yachter.courses.views.course_list', name='course-list-map'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'', include(admin.site.urls)),
)
