from django.contrib.gis.db import models
from django.conf import settings
import pytz

from yachter.utils import JSONField

class Source(models.Model):
    name = models.CharField(max_length=200, unique=True)
    implementation_class = models.CharField(max_length=200)
    params = JSONField(blank=True)
    
    def __unicode__(self):
        return self.name

    def get_implementation(self):
        o = __import__(self.implementation_class.rsplit('.', 1)[0])
        for c in self.implementation_class.split('.')[1:]:
            o = getattr(o, c)
        params = dict([(str(k),v) for k,v in self.params.items()])
        return o(**params)
    
    def get_observations(self, stations=None, save=True):
        source_class = self.get_implementation()
        if stations:
            station_map = dict([(s.source_key, s) for s in stations])
            results = source_class.query(station_map.keys())
        else:
            results = source_class.query(self.stations.values_list('source_key', flat=True))
        
        obs = []
        for r in results:
            if stations:
                station = station_map.get(r['station_id'])
                if not station:
                    continue
            else:
                station = Station.objects.get(source_key=r['station_id'], source=self)
                
            ob = Observation(station=station)
            for k,v in r.items():
                if k != 'station_id':
                    setattr(ob, k, v)
            obs.append(ob)
            if save:
                ob.save()
        
        return obs

class Station(models.Model):
    name = models.CharField(max_length=200, unique=True)
    source = models.ForeignKey(Source, related_name='stations')
    source_key = models.CharField(max_length=400, blank=True)
    location = models.PointField(srid=4326)
    interval = models.IntegerField(help_text="Seconds", default=60)
    
    objects = models.GeoManager()
    
    class Meta:
        unique_together = ('source', 'source_key',)
    
    def __unicode__(self):
        return self.name

class Observation(models.Model):
    station = models.ForeignKey(Station, related_name='observations')
    time = models.DateTimeField(help_text='UTC')
    wind_direction = models.IntegerField()
    wind_speed = models.FloatField()
    gust_speed = models.FloatField(null=True)
    pressure = models.FloatField(null=True)
    temp = models.FloatField(null=True)
    
    def __unicode__(self):
        return "%s@%s" % (self.station, self.time.isoformat())
    
    @property
    def local_time(self):
        return self.time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(settings.LOCAL_TIME_ZONE))
    
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
        return self.time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(settings.LOCAL_TIME_ZONE))
    
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

