from django import forms
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.util import unquote
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db import transaction, models
from django.forms.formsets import all_valid
from django.http import Http404
from django.template.defaultfilters import slugify
from django.utils.encoding import force_unicode
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect

from directseo.seo.models import SeoSite

from saved_search.models import SavedSearch

csrf_protect_m = method_decorator(csrf_protect)


class SavedSearchForm(forms.ModelForm):
        
    name = forms.CharField(label="Name", required=True,
                           help_text=("""
                                      A concise and descriptive
                                      name for this saved
                                      search, e.g.:
                                      us-nursing,
                                      texas-tech-support
                                      """))
    title = forms.CharField(label="Title", required=False,
                            help_text=("""A comma-separated list of job titles
                                       to search on. Terms entered here will
                                       refer to job titles as provided in your
                                       company's job listings. e.g.:
                                       Dental Technician,Office Assistant
                                       """))
    keyword = forms.CharField(label="Keywords", required=False,
                              help_text=("""
                                         A comma-separated list of keywords to
                                         search on, e.g.:
                                         nursing,phlebotomy
                                          """))

    location = forms.CharField(label="Location", required=False,
                               help_text=("""
                                          Type in the name of a country, state,
                                          region, city, etc., to search on, e.g.
                                          "New Delhi", "Canada", "Florida"
                                          """))
    

    def __init__(self, data=None, user=None, *args, **kwargs):
        # It will filter the group based on the user.
        super(SavedSearchForm, self).__init__(data, *args, **kwargs)
        if not user.is_superuser:
            groups = [g.id for g in user.groups.all()]
            grp_qs = Group.objects.filter(id__in=groups)
            site_ids = []
            for group in grp_qs:
                site_ids += [s.id for s in group.seosite_set.all()]
                
                sites = SeoSite.objects.filter(id__in=site_ids)
                if 'site' not in self.fields:
                    self.fields['site'] = forms.ModelMultipleChoiceField(
                        queryset=sites)
                else:
                    # If the form already has the 'site' field, it will simply
                    # set the querystring for the existing field to our dynamic
                    # querystring. Otherwise every time it is initialized via
                    # __init__ its queryset will be set back to
                    # Group.objects.all() which is undesired behavior.
                    self.fields['site'].queryset = sites

    class Meta:
        model = SavedSearch
        exclude = ("name_slug", "querystring", "group", "url_slab", "country",
                   "city", "state")
        fields = ("name", "location", "title", "keyword", "blurb", "show_blurb",
                  "show_production", "site")


