from django.contrib import admin

from directseo.seo.models import BusinessUnit
from saved_search.models import SavedSearch


class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_updated', 'keyword', 'title')
    search_fields = ['country__name', 'state__name', 'city__name', 'keyword',
                     'title']
    exclude = ('group',)

    def queryset(self, request):
        qs = super(SavedSearchAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(buid__in=request.user.groups.all())
            
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == 'buid':
                kwargs['queryset'] = BusinessUnit.objects\
                                                 .filter(user=request.user)
        return super(SavedSearchAdmin, self).formfield_for_manytomany(db_field,
                                                                      request,
                                                                      **kwargs)

    def last_updated(self, obj):
        return str(obj.date_created)
    last_updated.short_description = 'Last Updated'

        
admin.site.register(SavedSearch, SavedSearchAdmin)
