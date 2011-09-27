from django.contrib.auth.models import User
from django.db import models

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
    country_filter = models.TextField(null=True, blank=True)
    state_filter = models.TextField(null=True, blank=True)
    city_filter = models.TextField(null=True, blank=True)
    keyword_filter = models.TextField(null=True, blank=True)
    title_filter = models.TextField(null=True, blank=True)
    career_filter = models.TextField(null=True, blank=True)

    def full_querystring(self):
        fields = [date_created, country_filter, state_filter, city_filter,
                  keyword_filter, title_filter, career_filter]
        qs = ''
        for i in range(len(fields)):
            if fields[i] != fields[-1]:
                qs += '%s+AND+' % fields[i]
            else:
                qs += '%s' % fields[i]

        return qs
    

class Country(models.Model):
    """
    Represents a country in the world.

    """
    name = models.CharField(max_length=100)
    shortname = models.CharField(max_length=3)
    
    def save(self, *args, **kwargs):
        super(Country, self).save(*args, **kwargs, using='geodata')


class State(models.Model):
    """
    Represents a state in the world.

    """
    country = models.OneToOneField(Country)
    name = models.CharField(max_length=100)
    shortname = models.CharField(max_length=3)

    def save(self, *args, **kwargs):
        super(State, self).save(*args, **kwargs, using='geodata')
        

class City(models.Model):
    """
    Represents a city in the world.

    """
    state = models.OneToOneField(State)
    name = models.CharField(max_length=100)
    shortname = models.CharField(max_length=3)
    
    def save(self, *args, **kwargs):
        super(City, self).save(*args, **kwargs, using='geodata')