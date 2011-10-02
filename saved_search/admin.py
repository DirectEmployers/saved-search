from django.contrib import admin

from saved_search.models import SavedSearch


class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_updated', 'keyword', 'title')
    search_fields = ['country__name', 'state__name', 'city__name', 'keyword',
                     'title']

    def formfield_for_choice_field(self, db_field, **kwargs):
        if db_field.name == 'country':
            print 'foo'

    def last_updated(self):
        return str(obj.date_created)
    last_updated.short_description = 'Last Updated'

        
admin.site.register(SavedSearch, SavedSearchAdmin)
