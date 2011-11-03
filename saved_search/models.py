import re

from django.contrib.auth.models import User, Group
from django.db import models
from django.template.defaultfilters import slugify

from haystack.query import SearchQuerySet

from taggit.managers import TaggableManager

from directseo.seo.models import (jobListing, BusinessUnit, City, Country,
                                  State, SeoSite)


SOLR_ESCAPE_CHARS = ['+', '-', '&&', '||', '!', '(', ')', '{', '}', '[', ']',
                     '^', '"', '~', '*', '?']


class BaseSavedSearch(models.Model):
    name = models.CharField(max_length=100,
                            help_text=("""A concise and descriptive name for
                                       this saved search, e.g.: Nursing Jobs,
                                       Tech Support Jobs in Texas"""))
    name_slug = models.SlugField(max_length=100, blank=True, null=True)
    date_created = models.DateField(auto_now=True)
    querystring = models.CharField(max_length=2000, null=True, blank=True)
    title = models.CharField(max_length=800, null=True, blank=True,
                             help_text=("""
                                        A comma-separated list of job titles to
                                        search on. Terms entered here will refer
                                        to job titles as provided in your
                                        company's job listings. e.g.:
                                        Dental Technician,Office Assistant
                                        """))
    url_slab = models.CharField(max_length=255, null=True, blank=True)
    blurb = models.TextField(null=True, blank=True)
    show_blurb = models.BooleanField("Use Saved Search Blurb", default=True)
    show_production = models.BooleanField("Show in Production", default=False)
    
    def __unicode__(self):
        return '%s' % self.name

    def _attr_dict(self):
        raise NotYetImplementedError

    def get_sqs(self, *args, **kwargs):
        raise NotYetImplementedError

    def _escape(self, param):
        for c in SOLR_ESCAPE_CHARS:
            param = param.replace(c, '')
        param = param.replace(':', '\\:')
        return param

    def _make_qs(self, field, params):
        """
        Generates the query string which will be passed to Solr directly.
        
        """
        # If no parameter was passed in, immediately dump back out.
        if not params:
            return ''

        params = params.split(',')
        qs = []
        joinstring = ' OR '
            
        for thing in params:
            qs.append('%s:%s' % (field, self._escape(thing)))

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
        abstract = True
        

class SavedSearch(BaseSavedSearch):
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
    group = models.ForeignKey(Group, blank=True, null=True)
    site = models.ManyToManyField(SeoSite, blank=False, null=True)
    country = models.CharField(max_length=800, null=True, blank=True)
    state = models.CharField(max_length=800, null=True, blank=True)
    city = models.CharField(max_length=800, null=True, blank=True)
    keyword = TaggableManager()
    # keyword = models.CharField(max_length=800, null=True, blank=True,
    #                            help_text=("""
    #                                       A comma-separated list of keywords to
    #                                       search on, e.g.:
    #                                       nursing,phlebotomy
    #                                       """))

    def __unicode__(self):
        return '%s' % self.name

    def _attr_dict(self):
        return {'title': self.title, 'country': self.country,
                'state': self.state, 'text': self.keyword,
                'city': self.city}
        
    def clean(self):
        countries = self._make_qs('country', self.country)
        states = self._make_qs('state', self.state)
        cities = self._make_qs('city', self.city)
        titles = self._make_qs('title', self.title)
        bu = [s.business_units.all() for s in self.site.all()]
        # Create a single BusinessUnit out of the list of BusinessUnits
        # returned by the list comprehension on the previous line, if
        # it is a non-empty list.
        if bu:
            bu = ','.join([str(b.id) for b in reduce(lambda x,y: x|y, bu)])

        buids = self._make_qs('buid', bu)
        self.querystring = self._full_qs(self, [countries, states, cities,
                                                titles, buids])
        self.name_slug = slugify(self.name)
        self.url_slab = '%s/new-jobs::%s' % (self.name_slug, self.name)
        
    def get_sqs(self):
        """
        Returns the SearchQuerySet object generated by self.querystring
        when passed to the Solr backend.

        """
        keywords = self._keyword_sq(self.keyword)
        sqs = SearchQuerySet().models(jobListing).narrow(self.querystring)
        for kw in keywords:
            if kw:
                sqs = sqs.filter(text=kw)
        return sqs

    def _keyword_sq(self, keyword):
        """
        Handles the obj.keyword paramater since we need explicitly to consume
        this value with a .filter() call. This method will automatically
        seek exact match if there is one or more spaces in the value.
        
        """
        params = keyword.split(',')
        for param in params:
            p = param
            param = self._escape(param)
            if "#@#" in param:
                params.remove(p)
                params += param.split("#@#")
            else:
                params[params.index(p)] = param.strip(' ')

        return params

    class Meta:
        verbose_name = 'Saved Search'
        verbose_name_plural = 'Saved Searches'
        
