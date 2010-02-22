import csv
import math

from django.contrib.gis.db import models
from django.contrib.gis.measure import D
from django.contrib.gis.geos import LineString, Point

from utils import wind_angle_measure, bearing

SRID = 2193

class Mark(models.Model):
    name = models.CharField(max_length=200)
    location = models.PointField(srid=SRID)
    is_home = models.BooleanField(default=False)
    
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
        ]
        r += ["Quality %03d" % w for w in range(0, 360, 30)]
        csv_w.writerow(r)
        for c in queryset:
            r = [
                c.number,
                c.description,
                int(c.length * 10.0) / 10.0, # 0.1Nm accuracy
                'Y' if c.can_shorten else 'N',
            ]
            r += [c.quality(w) for w in range(0, 360, 30)]
            csv_w.writerow(r)

class Course(models.Model):
    BEAT_RANGE = 20.0
    RUN_RANGE = 20.0
    
    number = models.IntegerField(unique=True)
    marks = models.ManyToManyField(Mark, through='CourseMark')
    suitable_conditions = models.TextField(blank=True)
    unsuitable_conditions = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    
    objects = CourseManager()
    
    class Meta:
        ordering = ('number',)
    
    def __unicode__(self):
        return u"Course %d" % self.number
    
    @property
    def path(self):
        points = map(lambda cm: cm.mark.location, self.coursemark_set.all())
        path = LineString(*points)
        path.srid = SRID
        return path
    
    @property
    def length(self):
        return D(m=self.path.length).nm

    def get_length_display(self):
        return "%0.1f" % self.length
    get_length_display.short_description = 'Length (Nm)'

    def quality(self, wind):
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
    
    @property
    def can_shorten(self):
        marks = list(self.coursemark_set.all())[1:-1]
        home_marks = filter(lambda cm: cm.mark.is_home, marks)
        return len(home_marks) > 0
    
    @property
    def description(self):
        parts = [u"Start"]
        marks = list(self.coursemark_set.all())[1:-1]
        for cm in marks:
            if not cm.is_waypoint:
                parts.append(unicode(cm))
        parts.append(u"to finish.")
        return u", ".join(parts)
    
    @property
    def json(self):
        return {
            'id': self.id,
            'number': self.number,
            'path': self.path.wkt,
            'path_globalMercator': self.path.transform(900913, True).wkt,
            'marks': [cm.json for cm in self.coursemark_set.all() if not cm.is_waypoint],
            'length': self.length,
            'description': self.description,
            'can_shorten': self.can_shorten,
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
        >>> c = Course.objects.create(number=-1)
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
            cur = prev
        return d or None
    
    @property
    def distance_next(self):
        """
        >>> c = Course.objects.create(number=-2)
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