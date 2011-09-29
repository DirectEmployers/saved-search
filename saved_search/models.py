from django.contrib.auth.models import User
from django.db import models

from countria.models import *

from directseo.seo.models import BusinessUnit


class SavedSearch(models.Model):
    """
    Represents the data in a saved search.

    The fields themselves represent the query string passed to Solr, e.g.:
    ?q=buid:2852+AND+state:indiana
    
    """
    def __unicode__(self):
        return '%s :=> query=[]'

    name = models.CharField(max_length=100)    
    date_created = models.DateField(auto_now=True)
    country = models.ForeignKey(Country)
    state = models.ForeignKey(State)
    city = models.ForeignKey(City)
    keyword = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)

    def country_qs(self):
        return "country:%s" % self.country
        
    def state_qs(self):
        return "state:%s" % self.state

    def city_qs(self):
        return "city:%s" % self.city

    def keyword_qs(self):
        return "keyword:%s" % self.keyword

    def title_qs(self):
        return "title:%s" % self.title


    class Meta:
        verbose_name = 'Saved Search'
        verbose_name_plural = 'Saved Searches'
        
    

    