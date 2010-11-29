from datetime import datetime, timedelta
import urllib2
import time

from django.http import HttpResponse
from django.utils import simplejson as json
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.cache import cache
import pytz

from yachter.weather.models import Tide, Station

def tides(request, hours_past=6, hours_future=24):
    t = datetime.utcnow()
    t0 = t - timedelta(hours=hours_past)
    t1 = t + timedelta(hours=hours_future)
    
    r = {
        'results': [] 
    }
    for tide in Tide.objects.filter(time__gte=t0, time__lte=t1):
        r['results'].append({
            'id': tide.id,
            'time': tide.local_time.isoformat(),
            'height': tide.height,
            'type': tide.get_type_display().lower(),
        })
    
    return HttpResponse(json.dumps(r), content_type="application/json")

def tide_heights(request, hours_past=3, hours_future=6):
    t = datetime.utcnow()
    
    t_r = t + timedelta(minutes=7.5)
    t_r -= timedelta(minutes=t_r.minute % 10, seconds=t_r.second, microseconds=t_r.microsecond)
    
    t0 = t_r - timedelta(hours=hours_past)
    t1 = t_r + timedelta(hours=hours_future)
    
    tides_in = list(Tide.objects.filter(time__gt=t0, time__lt=t1))
    tides = [Tide.objects.previous(t0)] + tides_in + [Tide.objects.next(t1)]
    
    r = {
        'heights': {
            'pointStart': time.mktime(t0.utctimetuple()) * 1000,
            'pointInterval': 15 * 60 * 1000, # 15 mins
            'data': [],
        },
        'now': {
            'data': [
                [
                    time.mktime(t.utctimetuple()) * 1000,
                    Tide.objects.height_at(t)
                ],
            ]
        },
        'tides': {
            'data': [[time.mktime(tt.time.utctimetuple())*1000, tt.height] for tt in tides_in] 
        }
    }
    
    tc = t0
    tideIndex = 0
    while tc < t1:
        h = Tide.objects.height_between(tides[tideIndex], tides[tideIndex+1], tc)
        r['heights']['data'].append(h)
        
        tc += timedelta(minutes=15)
        if tides[tideIndex+1].time <= tc:
            tideIndex += 1
    
    return HttpResponse(json.dumps(r), content_type="application/json")
    
def station_list(request):
    r = {
        'stations': [],
    }
    for station in Station.objects.exclude(source__is_enabled=False):
        r['stations'].append(_station_info(station))
    
    return HttpResponse(json.dumps(r), content_type="application/json")
        
METRICS = ('wind_direction', 'wind_speed', 'gust_speed', 'pressure', 'temp')
def station_detail(request, station_id, history_hours=6):
    station = get_object_or_404(Station, pk=station_id)
    
    r = _station_info(station)
    
    # historical observations
    history_hours = float(request.GET.get('hours', history_hours))
    min_time = datetime.utcnow() - timedelta(hours=history_hours)
    observations = station.observations.filter(time__gte=min_time).order_by('time')
    
    r['history'] = dict([(m,[]) for m in METRICS])
    
    for ob in observations:
        for m in METRICS:
            v = getattr(ob, m)
            if v is not None:   # don't include nulls
                r['history'][m].append([
                    time.mktime(ob.time.utctimetuple()) * 1000,
                    v,
                ])
    
    return HttpResponse(json.dumps(r), content_type="application/json")

def _station_info(station):
    r = {
        'id': station.id,
        'name': station.name,
        'location': station.location.tuple,
        'latest': None,
        'source_credit': station.source.credit or station.source.name,
    }
    
    # latest observation
    obs = station.observations.order_by('-time')[:1]
    if obs:
        ob = obs[0]
        r['latest'] = {
            'id': ob.id,
            'time': time.mktime(ob.time.utctimetuple()) * 1000,
        }
        for m in METRICS:
            r['latest'][m] = getattr(ob, m)
    
    return r

def forecast(request):
    f = cache.get('Y:forecast')
    if not f:
        r = urllib2.urlopen(settings.FORECAST_URL)
        f = r.read()
        cache.set('Y:forecast', f, 3600)
        
    return HttpResponse(f, content_type="application/json")
    
    
 