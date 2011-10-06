from django.contrib.auth.models import User, Group
from django.db import models
from django.template.defaultfilters import slugify

from directseo.seo.models import BusinessUnit, City, Country, State


class SavedSearch(models.Model):

    def __unicode__(self):
        return '%s' % self.name

    name = models.CharField(max_length=100, help_text=("""
                                                       A concise and descriptive
                                                       name for this saved
                                                       search, e.g.:
                                                       Nursing Jobs,
                                                       Tech Support Jobs in
                                                       Texas
                                                       """))
    name_slug = models.SlugField(max_length=100, blank=True, null=True)
    group = models.ManyToManyField(Group, blank=True, null=True)
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
    
    def save(self, *args, **kwargs):
        # Calculate the slug value only on the first save, so that
        # any dependent URLs do not change.
        if not self.id:
            self.name_slug = slugify(self.name)

        countries = self._make_qs('country', obj.country.all())
        states = self._make_qs('state', obj.state.all())
        cities = self._make_qs('city', obj.city.all())
        keywords = self._make_qs('text', obj.keyword.split(','))
        titles = self._make_qs('title', obj.title.split(','))
        self.querystring = self._full_qs(obj, [countries, states, cities,
                                               keywords, titles])
        super(SavedSearch, self).save(*args, **kwargs)
    
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

    class Meta:
        verbose_name = 'Saved Search'
        verbose_name_plural = 'Saved Searches'
        
