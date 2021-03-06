# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'SavedSearch.group'
        db.delete_column('saved_search_savedsearch', 'group_id')

        # Adding field 'SavedSearch.country'
        db.add_column('saved_search_savedsearch', 'country', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'SavedSearch.state'
        db.add_column('saved_search_savedsearch', 'state', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'SavedSearch.city'
        db.add_column('saved_search_savedsearch', 'city', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Removing M2M table for field city on 'SavedSearch'
        db.delete_table('saved_search_savedsearch_city')

        # Removing M2M table for field country on 'SavedSearch'
        db.delete_table('saved_search_savedsearch_country')

        # Removing M2M table for field state on 'SavedSearch'
        db.delete_table('saved_search_savedsearch_state')

        # Adding M2M table for field group on 'SavedSearch'
        db.create_table('saved_search_savedsearch_group', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('savedsearch', models.ForeignKey(orm['saved_search.savedsearch'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('saved_search_savedsearch_group', ['savedsearch_id', 'group_id'])


    def backwards(self, orm):
        
        # Adding field 'SavedSearch.group'
        db.add_column('saved_search_savedsearch', 'group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'], null=True, blank=True), keep_default=False)

        # Deleting field 'SavedSearch.country'
        db.delete_column('saved_search_savedsearch', 'country')

        # Deleting field 'SavedSearch.state'
        db.delete_column('saved_search_savedsearch', 'state')

        # Deleting field 'SavedSearch.city'
        db.delete_column('saved_search_savedsearch', 'city')

        # Adding M2M table for field city on 'SavedSearch'
        db.create_table('saved_search_savedsearch_city', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('savedsearch', models.ForeignKey(orm['saved_search.savedsearch'], null=False)),
            ('city', models.ForeignKey(orm['seo.city'], null=False))
        ))
        db.create_unique('saved_search_savedsearch_city', ['savedsearch_id', 'city_id'])

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

        # Removing M2M table for field group on 'SavedSearch'
        db.delete_table('saved_search_savedsearch_group')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'saved_search.savedsearch': {
            'Meta': {'object_name': 'SavedSearch'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'querystring': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['saved_search']
