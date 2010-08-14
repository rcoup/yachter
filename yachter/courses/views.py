import StringIO

from django.contrib.gis import admin
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django import forms
from django.http import HttpResponse

from yachter.courses.models import Course
from yachter.courses.utils import export_static_zip

class CourseFindForm(forms.Form):
    wind = forms.IntegerField(label='Wind Direction (0-360)', min_value=0, max_value=360)
    include_laid_marks = forms.BooleanField(required=False, initial=False)

def course_find(request):
    c = {
        'title': 'Find Courses',
    }
    if 'wind' in request.GET:
        form = CourseFindForm(request.GET)
        if form.is_valid():
            wind = form.cleaned_data['wind'] % 360
            
            qs = Course.objects.all()
            if not form.cleaned_data.get('include_laid_marks', False):
                # exclude laid marks
                qs = qs.exclude(marks__is_laid=True)
            
            courses = list(qs)
            for course in courses:
                course.quality_wind = course.quality(wind)
        
            courses.sort(key=lambda x: x.length)
            courses.sort(key=lambda x: x.quality_wind, reverse=True)

            c['courses'] = courses
            c['wind'] = wind
    else:
        form = CourseFindForm()
    
    c['form'] = form

    return render_to_response('courses/course_find.html', c, context_instance=RequestContext(request))


def course_rankings(request):
    winds = range(0, 360, 30)
    courses = list(Course.objects.all())
    
    for course in courses:
        if course.path:
            course.quality_wind = [course.quality(w) for w in winds]
        else:
            course.quality_wind = ()
    courses.sort(key=lambda x: sum(x.quality_wind) / len(winds), reverse=True)
    
    c = {
        'courses': courses,
        'winds': winds,
    }
    return render_to_response('courses/course_rankings.html', c, context_instance=RequestContext(request))

def course_rankings_csv(request):
    f = StringIO.StringIO()
    Course.objects.export_csv(f)
    f.seek(0)

    r = HttpResponse(f, content_type='text/csv')
    r['Content-Disposition'] = 'attachment; filename=yachter_course_rankings.csv'
    return r

def export_zip(request):
    zf = StringIO.StringIO()
    
    export_static_zip(zf)
    zf.seek(0)
    
    r = HttpResponse(zf, content_type='application/zip')
    r['Content-Disposition'] = 'attachment; filename=yachter_courses_html.zip'
    return r

