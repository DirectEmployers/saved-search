from django.contrib import admin


class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ('name', 'buid', 'last_updated')

    def get_form(self, request, obj=None, **kwargs):
        form = super(SavedSearchAdmin, self).get_form(request, obj, **kwargs)
        self.fieldsets = [
            ('Basic Information', {'fields': [('name', 'last_updated')]}),
            ('Search Terms', {'fields': [('countries', 'states', 'cities',
                                          'keywords', 'titles', 'careers')]})
        ]
            
        

    def last_updated(self):
        return str(obj.date_created)
    last_updated.short_description = 'Last Updated'

        
#admin.site.register(SavedSearch, SavedSearchAdmin)