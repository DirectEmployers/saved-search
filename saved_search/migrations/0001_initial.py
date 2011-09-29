# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SavedSearch'
        db.create_table('saved_search_savedsearch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('date_created', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['countria.Country'])),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['countria.State'])),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['countria.City'])),
            ('keyword', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('saved_search', ['SavedSearch'])


    def backwards(self, orm):
        
        # Deleting model 'SavedSearch'
        db.delete_table('saved_search_savedsearch')


    models = {
        'countria.city': {
            'Meta': {'object_name': 'City'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['countria.Country']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'default': "'0.0'", 'max_digits': '9', 'decimal_places': '6'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'default': "'0.0'", 'max_digits': '9', 'decimal_places': '6'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'population': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['countria.State']", 'null': 'True'})
        },
        'countria.continent': {
            'Meta': {'unique_together': "(('name', 'code'),)", 'object_name': 'Continent'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        'countria.country': {
            'Meta': {'object_name': 'Country'},
            'capital': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'country_capital'", 'null': 'True', 'to': "orm['countria.City']"}),
            'continent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['countria.Continent']", 'null': 'True'}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['countria.Currency']", 'null': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idc': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'iso_2': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'iso_3': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True'}),
            'iso_number': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'default': "'0.0'", 'max_digits': '9', 'decimal_places': '6'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'default': "'0.0'", 'max_digits': '9', 'decimal_places': '6'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'population': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'sovereignty': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['countria.Country']", 'null': 'True'}),
            'tld': ('django.db.models.fields.CharField', [], {'max_length': '7', 'null': 'True'})
        },
        'countria.currency': {
            'Meta': {'unique_together': "(('name', 'code'),)", 'object_name': 'Currency'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        'countria.state': {
            'Meta': {'object_name': 'State'},
            'capital': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'state_capital'", 'null': 'True', 'to': "orm['countria.City']"}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'state_country'", 'null': 'True', 'to': "orm['countria.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'default': "'0.0'", 'max_digits': '9', 'decimal_places': '6'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'default': "'0.0'", 'max_digits': '9', 'decimal_places': '6'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'saved_search.savedsearch': {
            'Meta': {'object_name': 'SavedSearch'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['countria.City']"}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['countria.Country']"}),
            'date_created': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['countria.State']"}),
            'title': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['saved_search']
