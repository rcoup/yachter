from django.contrib.gis import admin
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from yachter.courses.models import Course, Mark, CourseMark

class MarkAdmin(admin.OSMGeoAdmin):
    list_display = ('name',)
    ordering = ('name',)

class CourseMarkInline(admin.TabularInline):
    model = CourseMark
    extra = 6

class CourseAdmin(admin.ModelAdmin):
    list_display = ('number', 'map_link', 'get_length_display', 'get_shortened_length_display', 'description',)
    inlines = [
        CourseMarkInline,
    ]
    ordering = ('number',)
    fieldsets = (
        (None, {
            'fields': ('number', 'suitable_conditions', 'unsuitable_conditions', 'comments'),
        }),
        ('Calculated Fields (change marks & save to update)', {
            'fields': ('get_length_display', 'can_shorten', 'get_shortened_length_display', 'description'),
        }),
    )
    readonly_fields = ('can_shorten', 'description', 'get_length_display', 'get_shortened_length_display',)

    def get_urls(self):
        urls = super(CourseAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^map/$', self.admin_site.admin_view(self.list_map)),
            url(r'^(\d+)/map/$', self.admin_site.admin_view(self.course_map)),
            url(r'^map/data/marks.json/?$', self.admin_site.admin_view(self.marks_json)),
            url(r'^map/data/course_(\d+).json/?$', self.admin_site.admin_view(self.course_json)),
        )
        return my_urls + urls

    def map_link(self, obj):
        return '<a href="%d/map/">Map</a>' % obj.id
    map_link.short_description = 'View Map'
    map_link.allow_tags = True

    def course_map(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        c = {
            'title': unicode(course),
            'current_app': self.admin_site.name,
            'course': course,
            'course_json': simplejson.dumps(course.json),
        }
        
        return render_to_response('admin/courses/course/map.html', c, context_instance=RequestContext(request))

    def list_map(self, request):
        c_qs = Course.objects.all();
        c_json = {}
        for c in c_qs:
            c_json[c.id] = c.json

        m_json = {}
        for m in Mark.objects.all():
            m_json[m.id] = m.json

        context = {
            'title': 'Courses Map',
            'current_app': self.admin_site.name,
            'courses': c_qs,
            'courses_json': simplejson.dumps(c_json),
            'marks_json': simplejson.dumps(m_json),
        }

        return render_to_response('admin/courses/course/list_map.html', context, context_instance=RequestContext(request))
      
    def marks_json(self, request):
        m_json = {}
        for m in Mark.objects.all():
            m_json[m.id] = m.json
        return HttpResponse(simplejson.dumps(m_json), content_type='application/json')
    
    def course_json(self, request, course_id):
        c = Course.objects.get(pk=course_id)
        return HttpResponse(simplejson.dumps(c.json), content_type='application/json')
        
admin.site.register(Course, CourseAdmin)
admin.site.register(Mark, MarkAdmin)
