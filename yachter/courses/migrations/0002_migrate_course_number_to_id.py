
from south.db import db
from django.db import models
from yachter.courses.models import *

class Migration:
    
    def forwards(self, orm):
        "Make Course.id == Course.number"
        sql = """
            SET CONSTRAINTS "courses_coursemark_course_id_fkey" DEFERRED;
            UPDATE "courses_coursemark" SET "course_id"="number" 
              FROM "courses_course" 
              WHERE "courses_course"."id" = "course_id";
            UPDATE "courses_course" SET "id"="number";
        """
        db.execute_many(sql)
    
    def backwards(self, orm):
        pass
    
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
