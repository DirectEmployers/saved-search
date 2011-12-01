from django import forms
from django.contrib.auth.models import Group
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from taggit.forms import TagField
from directseo.seo.models import SeoSite

from saved_search.models import SavedSearch

csrf_protect_m = method_decorator(csrf_protect)


class CustomTagField(TagField):
    label = "Keywords"
    

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
    keyword = TagField(label="Keywords", required=False)
                              
    # location = forms.CharField(label="Location", required=False,
    #                            help_text=("""Type in the name of a country, state,
    #                                       region, city, etc., to search on, e.g.
    #                                       "New Delhi", "Canada", "Florida"
    #                                       """))
    # new_keyword = TagField(label="Add Keyword (optional)",
    #                        required=False,
    #                        help_text=("""Please separate your new keywords
    #                                   with commas (e.g. "Waiter, Chef,
    #                                   Sous Chef, Maitre'd")"""))

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
        exclude = ("name_slug", "querystring", "group", "url_slab", "city",
                   "state", "country")
        fields = ("name", "title", "keyword", "blurb", "show_blurb",
                  "show_production", "site")


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=30,
                               widget=forms.PasswordInput(render_value=False))

