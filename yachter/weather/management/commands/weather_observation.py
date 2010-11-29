import sys
import time

from django.core.management.base import NoArgsCommand, make_option
from django.db.models import Min

class Command(NoArgsCommand):
    help = "Gets a new observation from each weather station"

    option_list = NoArgsCommand.option_list + (
        make_option('--loop', '-l', dest='loop', action="store_true", 
            default=False, help='Run continuously.'),
    )

    def handle_noargs(self, **options):
        from yachter.weather.models import Source, Station
        
        min_sleep = Station.objects.exclude(source__is_enabled=False).aggregate(Min('interval'))['interval__min']
        while True:
            for source in Source.objects.exclude(is_enabled=False):
                print >>sys.stderr, ("%s ..." % source),
                obs = source.get_observations()
                print >>sys.stderr, "%d observations" % len(obs)
                
            if not options['loop']:
                return
            
            try:
                print >>sys.stderr, "... sleeping for %ds..." % int(min_sleep)
                time.sleep(min_sleep)
            except KeyboardInterrupt:
                break
