from django.contrib.auth.models import User
from django.db import models

from directseo.seo.models import BusinessUnit, City, Country, State


class SavedSearch(models.Model):
    """
    Represents the data in a saved search.

    """
    def __unicode__(self):
        return '%s :=> query=[]'

    name = models.CharField(max_length=100)    
    date_created = models.DateField(auto_now=True)
    country = models.ManyToManyField(Country)
    state = models.ManyToManyField(State)
    city = models.ManyToManyField(City)
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
        
    

    
