from django.contrib import admin
from django import forms

from directseo.seo.models import BusinessUnit, Country, State, City
from saved_search.models import SavedSearch


class SearchAdmin(admin.AdminSite):
    pass

    
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


class SavedSearchForm(forms.ModelForm):
    name = forms.CharField(label="Name:", required=True,
                           help_text=("""
                                      A concise and descriptive
                                      name for this saved
                                      search, e.g.:
                                      us-nursing,
                                      texas-tech-support
                                      """))
    title = forms.CharField(label="Title:", required=False,
                            help_text=("""A comma-separated list of job titles
                                       to search on. Terms entered here will
                                       refer to job titles as provided in your
                                       company's job listings. e.g.:
                                       Dental Technician,Office Assistant
                                       """))
    keyword = forms.CharField(label="Name:", required=False,
                              help_text=("""
                                         A comma-separated list of keywords to
                                         search on, e.g.:
                                         nursing,phlebotomy
                                          """))
    country = forms.ModelMultipleChoiceField(queryset=Country.objects.all(),
                                             required=False, label="Countries:")
    state = forms.ModelMultipleChoiceField(queryset=State.objects.all(),
                                           required=False, label="States:")
    city = forms.ModelMultipleChoiceField(queryset=City.objects.all(),
                                          required=False, label="Cities:")
    

    class Meta:
        model = SavedSearch
        exclude = ("group",)
        
    
admin.site.register(SavedSearch, SavedSearchAdmin)
