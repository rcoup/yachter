from collections import defaultdict

from django.contrib.gis import admin
from django.contrib import messages
from django.db.models import Max

from yachter.weather.models import Tide, Source, Station, Observation

class TideAdmin(admin.ModelAdmin):
    date_hierarchy = 'time'

class ObservationInline(admin.TabularInline):
    model = Observation
    extra = 0
    max_num = 0
    ordering = ('-time',)
    fields = ('local_time', 'wind_direction', 'wind_speed', 'gust_speed', 'pressure', 'temp',)
    readonly_fields = ('local_time', 'wind_direction', 'wind_speed', 'gust_speed', 'pressure', 'temp',)
    
class StationAdmin(admin.OSMGeoAdmin):
    list_display = ('name', 'source', 'last_observation', 'interval')
    list_filter = ('source',)
    actions = ('query',)
    ordering = ('name',)
    inlines = (ObservationInline,)
    search_fields = ('name',)
    
    def last_observation(self, obj):
        return obj.observations.all().aggregate(Max('time'))['time__max']
    
    def query(self, request, queryset):
        by_source = defaultdict(list)
        for station in queryset:
            by_source[station.source_id].append(station)
        
        ob_count = 0
        for source in Source.objects.filter(id__in=by_source.keys()):
            obs = source.get_observations(by_source[source.id])
            ob_count += len(obs)
        
        messages.add_message(request, messages.INFO, '%d observations created' % ob_count)
        
    query.short_description = "Query selected stations"

class ObservationAdmin(admin.ModelAdmin):
    date_hierarchy = 'time'
    list_display = ('local_time', 'station', 'wind_direction', 'wind_speed', 'gust_speed', 'pressure', 'temp',)
    fields = ('time', 'local_time', 'station', 'wind_direction', 'wind_speed', 'gust_speed', 'pressure', 'temp',)
    readonly_fields = ('time', 'local_time', 'station', 'wind_direction', 'wind_speed', 'gust_speed', 'pressure', 'temp',)
    list_filter = ('time', 'station')
    ordering = ('-time',)

class StationInline(admin.TabularInline):
    model = Station
    fields = ('name', 'source_key', 'interval',)
    readonly_fields = ('name', 'source_key', 'interval',)
    extra = 0
    max_num = 0
    can_delete = False

class SourceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    inlines = (StationInline,)

admin.site.register(Tide, TideAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(Observation, ObservationAdmin)
