
from south.db import db
from django.db import models
from yachter.courses.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Mark'
        db.create_table('courses_mark', (
            ('id', orm['courses.Mark:id']),
            ('name', orm['courses.Mark:name']),
            ('location', orm['courses.Mark:location']),
            ('is_home', orm['courses.Mark:is_home']),
        ))
        db.send_create_signal('courses', ['Mark'])
        
        # Adding model 'Course'
        db.create_table('courses_course', (
            ('id', orm['courses.Course:id']),
            ('number', orm['courses.Course:number']),
            ('suitable_conditions', orm['courses.Course:suitable_conditions']),
            ('unsuitable_conditions', orm['courses.Course:unsuitable_conditions']),
            ('comments', orm['courses.Course:comments']),
        ))
        db.send_create_signal('courses', ['Course'])
        
        # Adding model 'CourseMark'
        db.create_table('courses_coursemark', (
            ('id', orm['courses.CourseMark:id']),
            ('course', orm['courses.CourseMark:course']),
            ('mark', orm['courses.CourseMark:mark']),
            ('rounding', orm['courses.CourseMark:rounding']),
            ('is_waypoint', orm['courses.CourseMark:is_waypoint']),
        ))
        db.send_create_signal('courses', ['CourseMark'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Mark'
        db.delete_table('courses_mark')
        
        # Deleting model 'Course'
        db.delete_table('courses_course')
        
        # Deleting model 'CourseMark'
        db.delete_table('courses_coursemark')
        
    
    
    models = {
        'courses.course': {
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marks': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['courses.Mark']"}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'suitable_conditions': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'unsuitable_conditions': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'courses.coursemark': {
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_waypoint': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'mark': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Mark']"}),
            'rounding': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'courses.mark': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_home': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '2193'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }
    
    complete_apps = ['courses']
