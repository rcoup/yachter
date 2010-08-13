# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Course.number'
        db.add_column('courses_course', 'number', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)
        
        # Update values to match Course.id
        for course in orm.Course.objects.all():
            course.number = course.id
            course.save()

        # Make Course.number unique
        db.alter_column('courses_course', 'number', self.gf('django.db.models.fields.IntegerField')(unique=True))
        
        # Changing field 'Course.id'
        db.execute_many("""
            DROP SEQUENCE IF EXISTS courses_course_id_seq;
            CREATE SEQUENCE courses_course_id_seq OWNED BY courses_course.id;
            SELECT setval('courses_course_id_seq', (SELECT MAX(id) FROM courses_course));
            ALTER TABLE courses_course ALTER COLUMN id SET DEFAULT nextval('courses_course_id_seq');
        """)

    def backwards(self, orm):
        
        # Deleting field 'Course.number'
        db.delete_column('courses_course', 'number')

        # Changing field 'Course.id'
        db.alter_column('courses_course', 'id', self.gf('django.db.models.fields.IntegerField')(primary_key=True))


    models = {
        'courses.course': {
            'Meta': {'ordering': "('id',)", 'object_name': 'Course'},
            '_quality_ratings': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'can_shorten': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marks': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['courses.Mark']", 'through': "orm['courses.CourseMark']", 'symmetrical': 'False'}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'path': ('django.contrib.gis.db.models.fields.GeometryField', [], {'srid': '2193', 'null': 'True', 'blank': 'True'}),
            'suitable_conditions': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'unsuitable_conditions': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'courses.coursemark': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'CourseMark'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_waypoint': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mark': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['courses.Mark']"}),
            'rounding': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'courses.mark': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Mark'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_home': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_laid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '2193'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['courses']
