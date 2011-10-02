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
            ('keyword', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('saved_search', ['SavedSearch'])

        # Adding M2M table for field buid on 'SavedSearch'
        db.create_table('saved_search_savedsearch_buid', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('savedsearch', models.ForeignKey(orm['saved_search.savedsearch'], null=False)),
            ('businessunit', models.ForeignKey(orm['seo.businessunit'], null=False))
        ))
        db.create_unique('saved_search_savedsearch_buid', ['savedsearch_id', 'businessunit_id'])

        # Adding M2M table for field country on 'SavedSearch'
        db.create_table('saved_search_savedsearch_country', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('savedsearch', models.ForeignKey(orm['saved_search.savedsearch'], null=False)),
            ('country', models.ForeignKey(orm['seo.country'], null=False))
        ))
        db.create_unique('saved_search_savedsearch_country', ['savedsearch_id', 'country_id'])

        # Adding M2M table for field state on 'SavedSearch'
        db.create_table('saved_search_savedsearch_state', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('savedsearch', models.ForeignKey(orm['saved_search.savedsearch'], null=False)),
            ('state', models.ForeignKey(orm['seo.state'], null=False))
        ))
        db.create_unique('saved_search_savedsearch_state', ['savedsearch_id', 'state_id'])

        # Adding M2M table for field city on 'SavedSearch'
        db.create_table('saved_search_savedsearch_city', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('savedsearch', models.ForeignKey(orm['saved_search.savedsearch'], null=False)),
            ('city', models.ForeignKey(orm['seo.city'], null=False))
        ))
        db.create_unique('saved_search_savedsearch_city', ['savedsearch_id', 'city_id'])


    def backwards(self, orm):
        
        # Deleting model 'SavedSearch'
        db.delete_table('saved_search_savedsearch')

        # Removing M2M table for field buid on 'SavedSearch'
        db.delete_table('saved_search_savedsearch_buid')

        # Removing M2M table for field country on 'SavedSearch'
        db.delete_table('saved_search_savedsearch_country')

        # Removing M2M table for field state on 'SavedSearch'
        db.delete_table('saved_search_savedsearch_state')

        # Removing M2M table for field city on 'SavedSearch'
        db.delete_table('saved_search_savedsearch_city')


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
