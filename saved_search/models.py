from django.contrib.auth.models import User, Group
from django.db import models
from django.template.defaultfilters import slugify

from directseo.seo.models import BusinessUnit, City, Country, State


class SavedSearch(models.Model):
    """
    
    
    """
    def __unicode__(self):
        return '<saved_search.SavedSearch object: %s>' % self.name

    name = models.CharField(max_length=100, help_text=("""
                                                       A concise and descriptive
                                                       name for this saved
                                                       search, e.g.:
                                                       Nursing Jobs,
                                                       Tech Support Jobs in
                                                       Texas
                                                       """))
    name_slug = models.SlugField(max_length=100, blank=True, null=True)
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
        # Calculate the slug value only on the first save, so that
        # any dependent URLs do not change.
        if not self.id:
            self.name_slug = slugify(self.name)
            
        super(SavedSearch, self).save(*args, **kwargs)
    

        

    class Meta:
        verbose_name = 'Saved Search'
        verbose_name_plural = 'Saved Searches'
        
