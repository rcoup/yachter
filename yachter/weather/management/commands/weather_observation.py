import sys
from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "Gets a new observation from each weather station"

    def handle(self, **options):
        from yachter.weather.models import Source
        
        for source in Source.objects.all():
            print >>sys.stderr, ("%s ..." % source),
            obs = source.get_observations()
            print >>sys.stderr, "%d observations" % len(obs)
