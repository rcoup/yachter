from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    url(r'^courses/course/find/$', 'yachter.courses.views.course_find', name='course-find'),
    url(r'^courses/course/rankings/$', 'yachter.courses.views.course_rankings', name='course-rankings'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'', include(admin.site.urls)),
)
