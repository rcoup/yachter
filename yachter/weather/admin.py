from django.contrib.gis import admin

from yachter.weather.models import Tide

class TideAdmin(admin.ModelAdmin):
    date_hierarchy = 'time'

admin.site.register(Tide, TideAdmin)
