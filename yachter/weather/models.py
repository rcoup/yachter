from django.contrib.gis.db import models
from django.conf import settings
import pytz

from yachter.utils import JSONField

class Source(models.Model):
    name = models.CharField(max_length=200, unique=True)
    implementation_class = models.CharField(max_length=200)
    params = JSONField()
    
    def __unicode__(self):
        return self.name

class Station(models.Model):
    name = models.CharField(max_length=200, unique=True)
    source = models.ForeignKey(Source)
    source_key = models.CharField(max_length=400, blank=True)
    location = models.PointField(srid=4326)
    interval = models.IntegerField(help_text="Seconds", default=60)
    
    def __unicode__(self):
        return self.name

class Observation(models.Model):
    station = models.ForeignKey(Station)
    time = models.DateTimeField()
    wind_direction = models.IntegerField()
    wind_speed = models.FloatField()
    gust_speed = models.FloatField(null=True)
    pressure = models.FloatField(null=True)
    temp = models.FloatField(null=True)
    
    def __unicode__(self):
        return "%s@%s" % (self.station, self.date.isoformat())
    
class Tide(models.Model):
    LOW = 0
    HIGH = 1
    CHOICES_TYPE = (
        (LOW, "Low"),
        (HIGH, "High"),
    )
    
    time = models.DateTimeField(help_text="UTC", unique=True)
    height = models.FloatField(help_text="Datum height in metres")
    type = models.IntegerField(choices=CHOICES_TYPE)
    
    class Meta:
        ordering = ('time',)

    def __unicode__(self):
        return u"%s: %s tide, %0.1f" % (self.local_time.strftime("%c"), self.get_type_display(), self.height)
    
    @property
    def local_time(self):
        return self.time.replace(tzinfo=pytz.timezone(settings.LOCAL_TIME_ZONE))
    
    @property
    def is_high(self):
        return (self.type == self.HIGH)

    @property
    def is_low(self):
        return (self.type == self.LOW)
    
    def next(self):
        return Tide.objects.filter(time__gt=self.time)[0]
    
    def previous(self):
        return Tide.objects.filter(time__lt=self.time).order_by('-time')[0]

