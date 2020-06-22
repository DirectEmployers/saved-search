from django.db import models

SOLR_ESCAPE_CHARS = ['+', '-', '&&', '||', '!', '(', ')', '{', '}', '[', ']',
                     '^', '~', '"', '*', '?']


class BaseSavedSearch(models.Model):
    name = models.CharField(max_length=100,
                            help_text=("""A concise and descriptive name for
                                       this saved search, e.g.: Nursing Jobs,
                                       Tech Support Jobs in Texas"""))
    name_slug = models.SlugField(max_length=100, blank=True, null=True)
    date_created = models.DateField(auto_now=True)
    querystring = models.CharField(max_length=16000, null=True, blank=True)
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

    #make specific text fields sortable as boolean objects in the admin panel
    querystring.char_as_boolean_filter = True
    blurb.char_as_boolean_filter = True
    
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
        
