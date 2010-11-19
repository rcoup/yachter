# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Source'
        db.create_table('weather_source', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, unique=True)),
            ('implementation_class', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('params', self.gf('yachter.utils.JSONField')()),
        ))
        db.send_create_signal('weather', ['Source'])

        # Adding model 'Station'
        db.create_table('weather_station', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, unique=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['weather.Source'])),
            ('source_key', self.gf('django.db.models.fields.CharField')(max_length=400, blank=True)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('interval', self.gf('django.db.models.fields.IntegerField')(default=60)),
        ))
        db.send_create_signal('weather', ['Station'])

        # Adding model 'Observation'
        db.create_table('weather_observation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('station', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['weather.Station'])),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
            ('wind_direction', self.gf('django.db.models.fields.IntegerField')()),
            ('wind_speed', self.gf('django.db.models.fields.FloatField')()),
            ('gust_speed', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('pressure', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('temp', self.gf('django.db.models.fields.FloatField')(null=True)),
        ))
        db.send_create_signal('weather', ['Observation'])

        # Adding model 'Tide'
        db.create_table('weather_tide', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(unique=True)),
            ('height', self.gf('django.db.models.fields.FloatField')()),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('weather', ['Tide'])


    def backwards(self, orm):
        
        # Deleting model 'Source'
        db.delete_table('weather_source')

        # Deleting model 'Station'
        db.delete_table('weather_station')

        # Deleting model 'Observation'
        db.delete_table('weather_observation')

        # Deleting model 'Tide'
        db.delete_table('weather_tide')


    models = {
        'weather.observation': {
            'Meta': {'object_name': 'Observation'},
            'gust_speed': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pressure': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['weather.Station']"}),
            'temp': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'wind_direction': ('django.db.models.fields.IntegerField', [], {}),
            'wind_speed': ('django.db.models.fields.FloatField', [], {})
        },
        'weather.source': {
            'Meta': {'object_name': 'Source'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'implementation_class': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True'}),
            'params': ('yachter.utils.JSONField', [], {})
        },
        'weather.station': {
            'Meta': {'object_name': 'Station'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval': ('django.db.models.fields.IntegerField', [], {'default': '60'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['weather.Source']"}),
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
