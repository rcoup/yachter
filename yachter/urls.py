from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    url(r'^courses/course/find/$', 'yachter.courses.views.course_find', name='course-find'),
    url(r'^courses/course/rankings/$', 'yachter.courses.views.course_rankings', name='course-rankings'),
    url(r'^courses/course/export/$', 'yachter.courses.views.export_zip', name='course-export-zip'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^doc/', include('django.contrib.admindocs.urls')),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}), 

    # Uncomment the next line to enable the admin:
    (r'', include(admin.site.urls)),
)
