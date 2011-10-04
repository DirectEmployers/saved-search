from django.contrib.auth.models import User, Group
from django.db import models

from directseo.seo.models import BusinessUnit, City, Country, State


class SavedSearch(models.Model):
    """
    Represents the data in a saved search.

    """
    def __unicode__(self):
        return '%s :=> query=[]' % self.name

    name = models.CharField(max_length=100, help_text=("""
                                                       A concise and descriptive
                                                       name for this saved
                                                       search, e.g.:
                                                       us-nursing,
                                                       texas-tech-support
                                                       """))
    group = models.ForeignKey(Group, blank=True, null=True)
    date_created = models.DateField(auto_now=True)
    country = models.ManyToManyField(Country, blank=True, null=True)
    state = models.ManyToManyField(State, blank=True, null=True)
    city = models.ManyToManyField(City, blank=True, null=True)
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
    def save(self, *args, **kwargs):
        self.country_qs = self.make_qs('country', self.country.all())
        self.state_qs = self.make_qs('state', self.state.all())
        self.city_qs = self.make_qs('city', self.city.all())
        self.title_qs = self.make_qs('title', self.title.split(','))
        self.keyword_qs = self.make_qs('text', self.keyword.split(','))
        super(SavedSearch, self).save(*args, **kwargs)
        
    def country_qs(self, field, params):
        qs = []
        for thing in params:
            if field in ('title', 'text'):
                joinstring = '+AND+'
                qs.append('%s:%s' % (field, thing))
            else:
                joinstring = '+OR+'
                qs.append('%s:%s' % (field, thing.name))
            
        return joinstring.join(qs)
        

    class Meta:
        verbose_name = 'Saved Search'
        verbose_name_plural = 'Saved Searches'
        
    

    
