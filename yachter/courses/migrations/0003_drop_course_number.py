
from south.db import db
from django.db import models
from yachter.courses.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Deleting field 'Course.number'
        db.delete_column('courses_course', 'number')
        
        # Changing field 'Course.id'
        # (to signature: django.db.models.fields.IntegerField(primary_key=True))
        db.alter_column('courses_course', 'id', orm['courses.course:id'])
        
    
    
    def backwards(self, orm):
        
        # Adding field 'Course.number'
        db.add_column('courses_course', 'number', orm['courses.course:number'])
        
        # Changing field 'Course.id'
        # (to signature: django.db.models.fields.AutoField(primary_key=True))
        db.alter_column('courses_course', 'id', orm['courses.course:id'])
        
    
    
    models = {
        'courses.course': {
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'marks': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['courses.Mark']"}),
            'suitable_conditions': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'unsuitable_conditions': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'courses.coursemark': {
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_waypoint': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'mark': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Mark']"}),
            'rounding': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'courses.mark': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_home': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '2193'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }
    
    complete_apps = ['courses']
