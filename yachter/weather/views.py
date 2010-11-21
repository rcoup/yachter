import datetime

from django.http import HttpResponse
from django.utils import simplejson as json

from yachter.weather.models import Tide, Station

def tides(self, hours_past=6, hours_future=24):
    t = datetime.datetime.utcnow()
    t0 = t - datetime.timedelta(hours=hours_past)
    t1 = t + datetime.timedelta(hours=hours_future)
    
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

def latest_observations(self):
    r = {
        'results': [],
    }
    for station in Station.objects.all():
        obs = station.observations.order_by('-time')[:1]
        if obs:
            ob = obs[0]
            r['results'].append({
                'id': ob.id,
                'time': ob.local_time.isoformat(),
                'wind_direction': ob.wind_direction,
                'wind_speed': ob.wind_speed,
                'gust_speed': ob.gust_speed,
                'pressure': ob.pressure,
                'temp': ob.temp,
                'station_id': station.id,
                'station_name': station.name,
                'station_location': station.location.tuple,
            })
    
    return HttpResponse(json.dumps(r), content_type="application/json")
            
            
