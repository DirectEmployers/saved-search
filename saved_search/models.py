import operator

from django.contrib.auth.models import Group
from django.db import models
from django.template.defaultfilters import slugify

from haystack.query import SearchQuerySet, SQ

from taggit.managers import TaggableManager
from taggit.models import Tag

from directseo.seo.models import jobListing, SeoSite


SOLR_ESCAPE_CHARS = ['+', '-', '&&', '||', '!', '(', ')', '{', '}', '[', ']',
                     '^', '~', '"', '*', '?']


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

    def get_sqs(self, *args, **kwargs):
        """Return a list of results."""
        raise NotImplementedError

    def _escape(self):
        """Escape special characters."""
        raise NotImplementedError

    def _make_qs(self):
        """Generate atomic elements of query."""
        raise NotImplementedError

    def _full_qs(self):
        """Combine the atomic elements of query into single query."""
        raise NotImplementedError

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

    def __unicode__(self):
        return '%s' % self.name

    def _attr_dict(self):
        kw = self.keyword.all()
        return {'title': self.title, 'country': self.country,
                'state': self.state, 'text': [self._drop_chars(t.name) for t in kw],
                'city': self.city}

    def _drop_chars(self, tag):
        for i in SOLR_ESCAPE_CHARS:
            tag = tag.replace(i, "")

        return tag
        
    def clean(self):
        if not self.pk:
            self.save()
        fields = ('country', 'state', 'city', 'title')
        self.name_slug = slugify(self.name)
        self.url_slab = '%s/new-jobs::%s' % (self.name_slug, self.name)
        
    def get_sqs(self):
        """
        Returns the SearchQuerySet object generated by self.querystring
        when passed to the Solr backend.

        """
        attrs = ("city", "state", "country", "title")
        bu = [s.business_units.all() for s in self.site.all()]

        if bu:
            bu = ','.join([str(b.id) for b in reduce(lambda x,y: x|y, bu)])

        sqs = SearchQuerySet().models(jobListing).narrow(self._make_qs('buid', bu))
        
        for a in attrs:
            attr = getattr(self, a)
            if attr:
                sqs = sqs.filter(SQ(("%s__exact" % a, attr)))

        kw = self.keyword.all()
        if kw:
            kwv = self.keyword.values()
            keywords = [self._escape(d['name']) for d in kwv if d['name']]
            for keyword in keywords:
                sqs = sqs.filter(text__exact=keyword)
                
        return sqs

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
        verbose_name = 'Saved Search'
        verbose_name_plural = 'Saved Searches'

