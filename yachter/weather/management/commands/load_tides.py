import sys
import csv
from datetime import datetime, date, time

import pytz
from django.core.management.base import LabelCommand
from django.db import transaction

class Command(LabelCommand):
    help = "Loads a CSV file of Tide data"
    args = "[csv]"
    label = 'LINZ-style tide csv file'

    @transaction.commit_on_success
    def handle_label(self, source_file, **options):
        from yachter.weather.models import Tide

        csv_r = csv.DictReader(open(source_file, 'rb'), 
            fieldnames=('day','weekday','month','year','time-0','height-0','time-1','height-1','time-2','height-2','time-3','height-3'))
    
        tz = pytz.FixedOffset(12*60) #NZST only
        
        # skip first 3x lines
        csv_iter = iter(csv_r)
        csv_iter.next()
        csv_iter.next()
        csv_iter.next()
        
        first_tide = None
        prev_tide_type = None
        for i,record in enumerate(csv_iter):
            t_date = date(int(record['year']), int(record['month']), int(record['day']))
            for j in range(4):
                f_time, f_height = 'time-%d' % j, 'height-%d' % j
                if record[f_time]:
                    t_time = time(*map(int, record[f_time].split(':')))
                    
                    t_datetime = datetime.combine(t_date, t_time)
                    print t_datetime
                    t_datetime = t_datetime.replace(tzinfo=tz)
                    
                    Tide.objects.filter(time=t_datetime).delete()
                    
                    tide = Tide()
                    tide.time = t_datetime.astimezone(pytz.UTC)
                    tide.height = float(record[f_height])
                    
                    print t_datetime, tide.time
                    
                    if i == 0:
                        first_tide = tide
                        continue
                    elif i == 1:
                        # save the previous one now we know whether it 
                        # is high or low
                        first_tide.type = Tide.LOW if tide.height > first_tide.height else Tide.HIGH
                        prev_tide_type = first_tide.type
                        first_tide.save()
                    
                    tide.type = Tide.LOW if prev_tide_type == Tide.HIGH else Tide.HIGH
                    prev_tide_type = tide.type
                    tide.save()
        
        print "Created %d tide entries" % (i+1)