# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'SavedSearch.keyword'
        db.alter_column('saved_search_savedsearch', 'keyword', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'SavedSearch.title'
        db.alter_column('saved_search_savedsearch', 'title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))


    def backwards(self, orm):
        
        # Changing field 'SavedSearch.keyword'
        db.alter_column('saved_search_savedsearch', 'keyword', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'SavedSearch.title'
        db.alter_column('saved_search_savedsearch', 'title', self.gf('django.db.models.fields.TextField')(null=True))


    models = {
        'saved_search.savedsearch': {
            'Meta': {'object_name': 'SavedSearch'},
            'buid': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['seo.BusinessUnit']", 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['seo.City']", 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['seo.Country']", 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'state': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['seo.State']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'seo.businessunit': {
            'Meta': {'object_name': 'BusinessUnit'},
            'associated_jobs': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date_crawled': ('django.db.models.fields.DateTimeField', [], {}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'primary_key': 'True'}),
            'scheduled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'seo.city': {
            'Meta': {'object_name': 'City'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'nation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['seo.Country']"})
        },
        'seo.country': {
            'Meta': {'object_name': 'Country'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'abbrev_short': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'seo.state': {
            'Meta': {'unique_together': "(('name', 'nation'),)", 'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'nation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['seo.Country']"})
        }
    }

    complete_apps = ['saved_search']
