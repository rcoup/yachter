import os
import shutil

from django.core.management.base import LabelCommand
from django.template.loader import render_to_string
from django.utils import simplejson
from django.conf import settings

class Command(LabelCommand):
    help = "Export a static HTML/JSON website for browsing the courses."
    args = "exportPath"
    label = 'path to export dir'

    def handle_label(self, export_path, **options):
        from yachter.courses.models import Course, Mark
        
        if not os.path.exists(os.path.join(export_path, 'data')):
            os.makedirs(os.path.join(export_path, 'data'))
        
        courses = Course.objects.all()
        for c in courses:
            f = open(os.path.join(export_path, 'data', 'course_%d.json' % c.id), 'wb')
            f.write(simplejson.dumps(c.json) + '\n')
            f.close()
        
        mark_json = {}
        for m in Mark.objects.all():
            mark_json[m.id] = m.json
            
        f = open(os.path.join(export_path, 'data', 'marks.json'), 'wb')
        f.write(simplejson.dumps(mark_json) + '\n')
        f.close()

        context = {
            'courses': courses,
        }
        html = render_to_string('courses/static_list.html', context)
        f = open(os.path.join(export_path, 'course_list.html'), 'wb')
        f.write(html)
        f.close()

        shutil.copy(os.path.join(settings.MEDIA_ROOT, 'course_list.js'), export_path)
