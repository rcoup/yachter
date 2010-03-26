# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from denorm import denorms

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding field 'Course.description'
        db.add_column('courses_course', 'description', self.gf('django.db.models.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'Course.can_shorten'
        db.add_column('courses_course', 'can_shorten', self.gf('django.db.models.NullBooleanField')(null=True, blank=True), keep_default=False)
    
        # Adding field 'Course.path'
        db.add_column('courses_course', 'path', self.gf('django.contrib.gis.db.models.GeometryField')(null=True, blank=True, srid=2193), keep_default=False)
    
        denorms.install_triggers()

    def backwards(self, orm):
        
        # Deleting field 'Course.description'
        db.delete_column('courses_course', 'description')

        # Deleting field 'Course.can_shorten'
        db.delete_column('courses_course', 'can_shorten')

        # Deleting field 'Course.path'
        db.delete_column('courses_course', 'path')
    
        denorms.install_triggers()
    
    models = {
        'courses.course': {
            'Meta': {'object_name': 'Course'},
            '_quality_ratings': ('django.db.models.TextField', [], {'null': True, 'blank': True}),
            'can_shorten': ('django.db.models.NullBooleanField', [], {'null': True, 'blank': True}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.TextField', [], {'null': True, 'blank': True}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'marks': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['courses.Mark']", 'through': "'CourseMark'"}),
            'path': ('django.contrib.gis.db.models.GeometryField', [], {'null': True, 'blank': True, 'srid': 2193}),
            'suitable_conditions': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'unsuitable_conditions': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'courses.coursemark': {
            'Meta': {'object_name': 'CourseMark'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_waypoint': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'mark': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Mark']"}),
            'rounding': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'courses.mark': {
            'Meta': {'object_name': 'Mark'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_home': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_laid': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '2193'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }
    
    complete_apps = ['courses']
