import datetime

from django.http import HttpResponse
from django.utils import simplejson as json

from yachter.weather.models import Tide

def tides(self, hours_past=6, hours_future=24):
    t = datetime.utcnow()
    t0 = t - datetime.timedelta(hours=hours_past)
    t1 = t + datetime.timedelta(hours=hours_future)
    
    r = []
    for tide in Tide.objects.filter(time__gte=t0, time__lte=t1):
        r.append({
            'time': tide.local_time.isoformat(),
            'height': tide.height,
            'type': tide.get_type_display().lower(),
        })
    
    return HttpResponse(json.dumps(r), content_type="application/json")
