from django.contrib.auth.models import User, Group
from django.db import models
from django.template.defaultfilters import slugify

from haystack.query import SearchQuerySet

from directseo.seo.models import BusinessUnit, City, Country, State, SeoSite


class SavedSearch(models.Model):
    """
    This model is a glorified string manipulation object. It takes a bunch
    of user input and calculates it into a querystring, then uses that
    querystring to return a SearchQuerySet object.

    Each SavedSearch object has a foreign key to an SeoSite object. This
    means that in order to create the same saved search across many SEO
    sites, the user will have to copy the saved search once for each site.

    This is made a bit easier by setting save_as == True in the ModelAdmin
    for this model. This allows the user to change the SEO site from the
    FK drop-down, then click "Save as New" to create a new Saved Search
    instance.
    
    """

    def __unicode__(self):
        return '%s' % self.name

    name = models.CharField(max_length=100,
                            help_text=("""
                                       A concise and descriptive name for this
                                       saved search, e.g.: Nursing Jobs, Tech
                                       Support Jobs in Texas
                                       """))
    name_slug = models.SlugField(max_length=100, blank=True, null=True)
    group = models.ManyToManyField(Group, blank=True, null=True)
    site = models.ForeignKey(SeoSite, blank=False, null=True)
    date_created = models.DateField(auto_now=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    keyword = models.CharField(max_length=255, null=True, blank=True,
                               help_text=("""
                                          A comma-separated list of keywords to
                                          search on, e.g.:
                                          nursing,phlebotomy
                                          """))
    title = models.CharField(max_length=255, null=True, blank=True,
                             help_text=("""
                                        A comma-separated list of job titles to
                                        search on. Terms entered here will refer
                                        to job titles as provided in your
                                        company's job listings. e.g.:
                                        Dental Technician,Office Assistant
                                        """))
    querystring = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)

    def clean(self):
        countries = self._make_qs('country', self.country)
        states = self._make_qs('state', self.state)
        cities = self._make_qs('city', self.city)
        keywords = self._make_qs('text', self.keyword)
        titles = self._make_qs('title', self.title)
        buids = self._make_qs('buid', ','.join([str(b.id) for b in
                                               self.site.business_units.all()]))
        self.querystring = self._full_qs(self, [countries, states, cities,
                                                keywords, titles, buids])
        self.name_slug = slugify(self.name)
        self.url = '%s/new-jobs' % self.name_slug
        
    def get_sqs(self):
        """
        Returns the SearchQuerySet object generated by self.querystring
        when passed to the Solr backend.

        """
        sqs = SearchQuerySet().narrow(self.querystring).load_all()
        return sqs
        
    def _make_qs(self, field, params):
        """
        Generates the query string which will be passed to Solr directly.
        
        """
        # If no parameter was passed in, immediately dump back out.
        if not params:
            return ''

        params = params.split(',')
        qs = []
        # All fields except full-text search, i.e. keyword search, are
        # sought disjunctively. In other words, if user wants all jobs
        # in Austin, Dallas and San Antonio, we want to search for all
        # jobs in Austin OR Dallas OR San Antonio. Otherwise, searching
        # conjunctively (AND) will result in only those jobs available
        # in ALL of those cities together. The difference between spoken
        # English and logical syntax.
        joinstring = ' OR '
            
        for thing in params:
            if field in ('title', 'text', 'buid'):
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

    class Meta:
        verbose_name = 'Saved Search'
        verbose_name_plural = 'Saved Searches'
        
