# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Observation.collected_at'
        db.add_column('weather_observation', 'collected_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2010, 1, 1)), keep_default=False)
        
        # Update collected_at values to match Observation.time
        for ob in orm.Observation.objects.all():
            ob.collected_at = ob.time
            ob.save()


    def backwards(self, orm):
        
        # Deleting field 'Observation.collected_at'
        db.delete_column('weather_observation', 'collected_at')


    models = {
        'weather.observation': {
            'Meta': {'ordering': "('-time',)", 'object_name': 'Observation'},
            'collected_at': ('django.db.models.fields.DateTimeField', [], {}),
            'gust_speed': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pressure': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'observations'", 'to': "orm['weather.Station']"}),
            'temp': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'wind_direction': ('django.db.models.fields.IntegerField', [], {}),
            'wind_speed': ('django.db.models.fields.FloatField', [], {})
        },
        'weather.source': {
            'Meta': {'object_name': 'Source'},
            'credit': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'implementation_class': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True'}),
            'params': ('yachter.utils.JSONField', [], {'blank': 'True'})
        },
        'weather.station': {
            'Meta': {'unique_together': "(('source', 'source_key'),)", 'object_name': 'Station'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval': ('django.db.models.fields.IntegerField', [], {'default': '60'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': "orm['weather.Source']"}),
            'source_key': ('django.db.models.fields.CharField', [], {'max_length': '400', 'blank': 'True'})
        },
        'weather.tide': {
            'Meta': {'ordering': "('time',)", 'object_name': 'Tide'},
            'height': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'unique': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['weather']
