import sys
import csv
import re

from django.core.management.base import LabelCommand

class Command(LabelCommand):
    help = "Loads a CSV file of Course data (Number,Course)"
    args = "[csv]"
    label = 'course csv file'

    def handle_label(self, source_file, **options):
        from yachter.courses.models import Course, CourseMark
        
        csv_r = csv.DictReader(open(source_file, 'rb'))
    
        for record in csv_r:
            print "#%s: '%s'" % (record['Number'], record['Course'])
            marks = self.build_course(record['Course'])
            if not marks:
                break
            
            course,created = Course.objects.get_or_create(id=record['Number'])
            CourseMark.objects.filter(course=course).delete()
            
            for mark,rounding in marks:
                cm = CourseMark(course=course, mark=mark, rounding=rounding)
                cm.save()
            print "Built course %s" % record['Number']

    def build_course(self, text):
        from yachter.courses.models import Mark
        
        # extra commas
        text = re.sub(r',\s*\(', ' (', text)
        
        parts = text.split(',')
        parts = map(str.strip, parts)
        parts = filter(len, parts)
        parts = map(str.lower, parts)
    
        course = []
        for p in parts:
            pm = re.match('([\w\s]+)\((\w+)\)', p)
            if pm:
                tm = pm.groups()[0].strip()
                td = pm.groups()[1].strip().upper()
            else:
                tm = p
                td = None
            
            # move random hacks elsewhere?
            if tm == "start":
                td = 'PORT'
                tm = "odm"
            elif "finish" in tm:
                td = 'STARBOARD'
                tm = "odm"
            
            # FIX TYPOS
            tm = re.sub('nth', 'north', tm)
            tm = re.sub('red ', '', tm)
            tm = re.sub('yellow ', '', tm)
            tm = re.sub('green ', '', tm)
        
            print "\t%s (%s)" % (tm, td),
            
            try:
                m = Mark.objects.get(name__iexact=tm)
            except Mark.DoesNotExist:
                for m in Mark.objects.all():
                    # HACKS
                    mn = m.name.lower()
                    if re.sub(' ', '', mn) == tm:
                        break
                    if re.sub('buoy', 'beacon', tm) == mn:
                        break
                    if re.sub(' buoy', '', tm) == mn:
                        break
                else:
                    print "**NOTFOUND**"
                    return False
            
            # duplicate marks?!
            if len(course) and course[-1] == (m, td):
                print "**DUPLICATE**"
                continue
            
            print "=> %d (%s)" % (m.id, m.name)
            course.append((m, td))
        
        return course
