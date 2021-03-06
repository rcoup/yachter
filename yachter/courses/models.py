import csv
import math
import operator

import django.db.models
import django.contrib.gis.db.models
from django.contrib.gis.db import models
from django.contrib.gis.measure import D
from django.contrib.gis.geos import LineString, Point
import denorm
from django.utils import simplejson
import south.introspection_plugins.geodjango

from utils import wind_angle_measure, bearing

SRID = 2193
WINDS = range(0, 360, 30)
WINDS_DETAILED = range(0, 360, 10)

class Mark(models.Model):
    name = models.CharField(max_length=200)
    location = models.PointField(srid=SRID)
    is_home = models.BooleanField(help_text='Is this a start/end mark', default=False)
    is_laid = models.BooleanField(help_text='Is this a laid mark', default=False)
    
    class Meta:
        ordering = ('name',)
    
    def __unicode__(self):
        return unicode(self.name)

    @property
    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location.wkt,
            'location_globalMercator': self.location.transform(900913, True).wkt,
        }

class CourseManager(models.Manager):
    def export_csv(self, output_file, queryset=None):
        if not queryset:
            queryset = self.get_query_set()
        
        csv_w = csv.writer(output_file)
        r = [
            "Number",
            "Description",
            "Length (Nm)",
            "Easy to Shorten?",
            "Shortened Length",
        ]
        r += ["Quality %03d" % w for w in WINDS]
        csv_w.writerow(r)
        for c in queryset:
            r = [
                c.number,
                c.description,
                int(c.length * 10.0) / 10.0, # 0.1Nm accuracy
                'Y' if c.can_shorten else 'N',
                int(c.shortened_length * 10.0) / 10.0 if c.can_shorten else '', # 0.1Nm accuracy
            ]
            r += [c.quality(w) for w in WINDS]
            csv_w.writerow(r)
    
    def finder_json(self, queryset=None):
        if not queryset:
            queryset = self.get_query_set()
        
        d = {
            "rankings": {},
            "courses": {}, 
        }
        for w in WINDS_DETAILED:
            dw = []
            for c in queryset:
                dw.append((c.quality(w), c))
                
            dw.sort(key=lambda x: x[1].length)
            dw.sort(key=operator.itemgetter(0), reverse=True)
            dw = map(lambda x: (x[0], x[1].id, x[1].has_laid_mark), dw)
            d['rankings'][w] = dw[:25]
        
        for c in queryset:
            d['courses'][c.id] = {
                "name": unicode(c),
                "length": c.get_length_display(),
                "can_shorten": c.can_shorten,
                "shortened_length": c.get_shortened_length_display(),
                "description": c.description,
            }
        
        return d

class Course(models.Model):
    BEAT_RANGE = 20.0
    RUN_RANGE = 20.0
    
    number = models.IntegerField('Number', unique=True)
    marks = models.ManyToManyField(Mark, through='CourseMark')
    suitable_conditions = models.TextField(blank=True)
    unsuitable_conditions = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    
    objects = CourseManager()
    
    class Meta:
        ordering = ('number',)
    
    def __unicode__(self):
        return u"Course %d" % self.number
    
    @denorm.denormalized(django.contrib.gis.db.models.fields.GeometryField, srid=SRID)
    @denorm.depend_on_related('Mark')    
    def path(self):
        points = map(lambda cm: cm.mark.location, self.coursemark_set.all())
        if len(points):
            path = LineString(*points)
            path.srid = SRID
            return path
    
    @property
    def length(self):
        if self.path:
            return D(m=self.path.length).nm
        else:
            return 0.0

    def get_length_display(self):
        return "%0.1f" % self.length
    get_length_display.short_description = 'Length (Nm)'

    @property
    def shortened_length(self):
        if self.can_shorten and self.path:
            points = []
            for i,cm in enumerate(self.coursemark_set.all()):
                points.append(cm.mark.location)
                if i > 0 and cm.mark.is_home:
                    break
            
            length = LineString(*points).length
            return D(m=length).nm
    
    def get_shortened_length_display(self):
        sl = self.shortened_length
        if sl:
            return "%0.1f" % sl
        else:
            return ""
    get_shortened_length_display.short_description = 'Shortened Length (Nm)'

    def quality(self, wind):
        wind = wind % 360
        if (wind % 30 == 0) and self._quality_ratings:
            # cached shortcut :)
            v = simplejson.loads(self._quality_ratings)[wind / 30]
            if v is not None:
                return v
        return self._quality(wind)
    
    @denorm.denormalized(django.db.models.TextField)
    @denorm.depend_on_related('Mark')    
    def _quality_ratings(self):
        return simplejson.dumps([self.quality(w) for w in WINDS])

    def _quality(self, wind):
        if self.path is None:
            return None
        
        beat_pc, beat_count = wind_angle_measure(self.path, wind, 0, self.BEAT_RANGE)
        run_pc, run_count = wind_angle_measure(self.path, wind, 180, self.RUN_RANGE)
        reach_pc, reach_count = 1.0 - beat_pc - run_pc, self.marks.count()-1 - beat_count - run_count
        
        vote = 0
        vote += min(beat_count, 2)
        vote += min(run_count, 2)
        vote += min(reach_count, 1)
        
        if vote < 5 and (beat_pc > 0.25 or run_pc > 0.25):
            vote += 1
        
        # print "\tWIND-ANGLES=", ", ".join([str(a) for a in self.wind_angles(wind)])
        # print "\tBEAT: ", beat_count, beat_pc
        # print "\tRUN: ", run_count, run_pc
        # print "\tREACH: ", reach_count, reach_pc
        # print "\tVOTE=", vote
        return vote
    
    def beat_percent(self, wind):
        return wind_angle_measure(self.path, wind, 0, self.BEAT_RANGE)[0]
        
    def run_percent(self, wind):
        return wind_angle_measure(self.path, wind, 180, self.RUN_RANGE)[0]
        
    def reach_percent(self, wind):
        return 1.0 - self.beat_percent - self.run_percent
    
    @property
    def bearings(self):
        b = []
        p_from = self.path[0]
        for p_to in self.path[1:]:
            b.append(int(bearing(p_from, p_to)))
            p_from = p_to
        return b
    
    def wind_angles(self, wind):
        return map(lambda b: ((b - wind) % 360) - 180, self.bearings)
    
    @denorm.denormalized(django.db.models.NullBooleanField)
    @denorm.depend_on_related('Mark')    
    def can_shorten(self):
        marks = list(self.coursemark_set.all())[1:-1]
        home_marks = filter(lambda cm: cm.mark.is_home, marks)
        return len(home_marks) > 0
    
    @denorm.denormalized(django.db.models.TextField)
    @denorm.depend_on_related('Mark')    
    def description(self):
        if not self.coursemark_set.count():
            return u""
        
        marks = list(self.coursemark_set.all())[1:-1]
        parts = [u"Start"]
        for cm in marks:
            if not cm.is_waypoint:
                parts.append(unicode(cm))
        parts.append(u"to finish.")
        return u", ".join(parts)
    
    @property
    def has_laid_mark(self):
        if not hasattr(self, '_has_laid_mark'):
            self._has_laid_mark = (self.marks.filter(is_laid=True).count() > 0)
        return self._has_laid_mark
    
    @property
    def json(self):
        return {
            'id': self.id,
            'number': self.number,
            'path': self.path.wkt if self.path else None,
            'path_globalMercator': self.path.transform(900913, True).wkt if self.path else None,
            'marks': [cm.json for cm in self.coursemark_set.all() if not cm.is_waypoint],
            'length': self.length,
            'description': self.description,
            'can_shorten': self.can_shorten,
            'shortened_length': self.shortened_length,
        }
    
class CourseMark(models.Model):
    ROUND_PORT = 'PORT'
    ROUND_STARBOARD = 'STARBOARD'
    CHOICES_ROUND = (
        (ROUND_PORT, 'Port'),
        (ROUND_STARBOARD, 'Starboard'),
    )
    
    course = models.ForeignKey(Course)
    mark = models.ForeignKey(Mark)
    rounding = models.CharField(max_length=10, choices=CHOICES_ROUND)
    is_waypoint = models.BooleanField(default=False, help_text='Just a waypoint to an actual mark?')
    
    class Meta:
        order_with_respect_to = 'course'

    def __unicode__(self):
        return u"%s (%s)" % (self.mark, self.get_rounding_display())
    
    @property
    def distance_previous(self):
        """
        >>> c = Course.objects.create(id=-1)
        >>> m1 = Mark.objects.create(location=Point(0,0), name='A')
        >>> m2 = Mark.objects.create(location=Point(100, 0), name='B')
        >>> cm1 = CourseMark.objects.create(course=c, mark=m1, rounding=CourseMark.ROUND_STARBOARD)
        >>> cm2 = CourseMark.objects.create(course=c, mark=m2, rounding=CourseMark.ROUND_STARBOARD)
        >>> cm3 = CourseMark.objects.create(course=c, mark=m1, rounding=CourseMark.ROUND_STARBOARD)
        >>> cm3.distance_previous == D(m=100).nm
        True
        >>> cm2.distance_previous == D(m=100).nm
        True
        >>> cm1.distance_previous == None
        True
        """
        d = 0
        cur = self
        while True:
            try:
                prev = cur.get_previous_in_order()
                d += D(m=cur.mark.location.distance(prev.mark.location)).nm
                if not prev.is_waypoint:
                    break
            except CourseMark.DoesNotExist:
                break
            
            if not prev.is_waypoint:
                break
            cur = prev
        return d or None
    
    @property
    def distance_next(self):
        """
        >>> c = Course.objects.create(id=-2)
        >>> m1 = Mark.objects.create(location=Point(0,0), name='A')
        >>> m2 = Mark.objects.create(location=Point(100, 0), name='B')
        >>> cm1 = CourseMark.objects.create(course=c, mark=m1, rounding=CourseMark.ROUND_STARBOARD)
        >>> cm2 = CourseMark.objects.create(course=c, mark=m2, rounding=CourseMark.ROUND_STARBOARD)
        >>> cm3 = CourseMark.objects.create(course=c, mark=m1, rounding=CourseMark.ROUND_STARBOARD)
        >>> cm1.distance_next == D(m=100).nm
        True
        >>> cm2.distance_next == D(m=100).nm
        True
        >>> cm3.distance_next == None
        True
        """
        d = 0
        cur = self
        while True:
            try:
                next = cur.get_next_in_order()
                d += D(m=cur.mark.location.distance(next.mark.location)).nm
                if not next.is_waypoint:
                    break
            except CourseMark.DoesNotExist:
                break
            
            if not next.is_waypoint:
                break
            cur = next
        return d or None
    
    @property
    def bearing_from_previous(self):
        b = 0.0
        c = 0.0
        cur = self
        #FIXME: weighted average based on distances
        while True:
            try:
                prev = cur.get_previous_in_order()
                b += bearing(prev.mark.location.tuple, cur.mark.location.tuple)
                c += 1
            except CourseMark.DoesNotExist:
                break

            if not prev.is_waypoint:
                break
            cur = prev
        return b/c if c else None
    
    @property
    def bearing_to_next(self):
        b = 0.0
        c = 0.0
        cur = self
        #FIXME: weighted average based on distances
        while True:
            try:
                next = cur.get_next_in_order()
                b += bearing(cur.mark.location.tuple, next.mark.location.tuple)
                c += 1
            except CourseMark.DoesNotExist:
                break
            
            if not next.is_waypoint:
                break
            cur = next
        return b/c if c else None
    
    @property
    def json(self):
        return {
            'id': self.id,
            'mark': self.mark.json,
            'rounding': self.rounding,
            'rounding_display': self.get_rounding_display(),
            'is_waypoint': self.is_waypoint,
        }