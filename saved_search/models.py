from django.contrib.auth.models import User
from django.db import models

from directseo.seo.models import BusinessUnit, City, Country, State


class SavedSearch(models.Model):
    """
    Represents the data in a saved search.

    """
    def __unicode__(self):
        return '%s :=> query=[]'

    name = models.CharField(max_length=100, help_text=("""
                                                       A concise and descriptive
                                                       name for this saved
                                                       search, e.g.:
                                                       us-nursing,
                                                       texas-tech-support
                                                       """))
    buid = models.ManyToManyField(BusinessUnit, blank=True, null=True)
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
        
    

    
