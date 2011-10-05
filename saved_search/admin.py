import simplejson

from django import forms
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from directseo.seo.models import BusinessUnit, Country, State, City
from saved_search.models import SavedSearch


class SavedSearchForm(forms.ModelForm):
    name = forms.CharField(label="Name", required=True,
                           help_text=("""
                                      A concise and descriptive
                                      name for this saved
                                      search, e.g.:
                                      us-nursing,
                                      texas-tech-support
                                      """))
    title = forms.CharField(label="Title", required=False,
                            help_text=("""A comma-separated list of job titles
                                       to search on. Terms entered here will
                                       refer to job titles as provided in your
                                       company's job listings. e.g.:
                                       Dental Technician,Office Assistant
                                       """))
    keyword = forms.CharField(label="Keywords", required=False,
                              help_text=("""
                                         A comma-separated list of keywords to
                                         search on, e.g.:
                                         nursing,phlebotomy
                                          """))
    locbool = forms.BooleanField(label="Add location filter", required=False)
    
    class Meta:
        model = SavedSearch
        exclude = ("group", "name_slug", "city", "state", "country",
                   "querystring")


class SavedSearchLocForm(forms.ModelForm):
    """
    Sub-form loaded when user checks 'locbool' checkbox on SavedSearchForm.
    
    """
    country = forms.ModelMultipleChoiceField(queryset=Country.objects.all(),
                                             required=False, label="Countries")
    state = forms.ModelMultipleChoiceField(queryset=State.objects.all(),
                                            required=False, label="States")
    city = forms.ModelMultipleChoiceField(queryset=City.objects.all(),
                                          required=False, label="Cities")

    class Meta:
        model = SavedSearch
        exclude = ("group", "name_slug", "title", "keyword", "name", "locbool")
    
        
class SavedSearchAdmin(admin.ModelAdmin):
    search_fields = ['country__name', 'state__name', 'city__name', 'keyword',
                     'title']

    def get_form(self, request, obj=None, **kwargs):
        return SavedSearchForm

    def get_urls(self):
        # See django docs on get_urls here
        # https://docs.djangoproject.com/en/dev/ref/contrib/admin/
        from django.conf.urls.defaults import patterns
        urls = super(SavedSearchAdmin, self).get_urls()
        my_urls = patterns('', (r'^ajax_loc/$', self.ajax_loc))

        return my_urls + urls

    def ajax_loc(self, request):
        country = request.GET.get('country')
        json = ''
        if country:
            states = State.objects.filter(nation=Country.objects.get(pk=country))
            json = simplejson.dumps(list(states))
        return HttpResponse(json, mimetype='application/json')
        
    def queryset(self, request):
        qs = super(SavedSearchAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(buid__in=request.user.groups.all())
            
    def save_model(self, request, obj, form, change):
        new_search = form.save()
        # Since country/state/city fields on the model are M2M fields, and
        # the querystring is calculated from these fields, at least in some
        # cases, we are using this receiver to handle the calculation of the
        # string.
        countries = self._make_qs('country', obj.country.all())
        states = self._make_qs('state', obj.state.all())
        cities = self._make_qs('city', obj.city.all())
        keywords = self._make_qs('text', obj.keyword.split(','))
        titles = self._make_qs('title', obj.title.split(','))
        n = SavedSearch.objects.get(pk=new_search.pk)
        n.querystring = self._full_qs(obj, [countries, states, cities,
                                                     keywords, titles])
        n.save()

    def last_updated(self, obj):
        return str(obj.date_created)
    last_updated.short_description = 'Last Updated'

    def _make_qs(self, field, params):
        """
        Generates the query string which will be passed to Solr directly.
        
        """
        # If no parameter was passed in, immediately dump back out.
        if not params:
            return ''
        qs = []
        # All fields except full-text search, i.e. keyword search, are
        # sought disjunctively. In other words, if user wants all jobs
        # in Austin, Dallas and San Antonio, we want to search for all
        # jobs in Austin OR Dallas OR San Antonio. Otherwise, searching
        # conjunctively (AND) will result in only those jobs available
        # in ALL of those cities together. The difference between spoken
        # English and logical syntax.
        joinstring = ' OR '
        if field == 'text':
            joinstring = ' AND '
            
        for thing in params:
            if field in ('title', 'text'):
                qs.append('%s:%s' % (field, thing))
            else:
                qs.append('%s:%s' % (field, thing.name))

        return joinstring.join(qs)  
    
    def _full_qs(self, instance, fields):
        """
        _full_qs(instance, fields)
        
        `instance': SavedSearch model instance
        `fields':   An iterable containing instance attributes you wish to
        include in the Solr querystring.
        
        Join all the query substrings from various fields into one
        'master' querystring for passage to Solr.
        
        """
        terms = []
        for attr in fields:
            if attr:
                terms.append(attr)
                
        # Using conjunction here since we want all job listings returned
        # to conform to each individual query term.
        return ' AND '.join(terms)


admin.site.register(SavedSearch, SavedSearchAdmin)
