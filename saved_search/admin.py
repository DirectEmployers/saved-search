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
    locbool = forms.BooleanField(label="Add location filter", required=False)

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
        exclude = ("name_slug", "city", "state", "country",
                   "querystring", "group")


class SavedSearchAdmin(admin.ModelAdmin):
    search_fields = ['country', 'state', 'city', 'keyword', 'title',
                     'site__name']
    list_display = ('name', 'last_updated', 'results')
    save_as = True

    def get_form(self, request, obj=None, **kwargs):
        return SavedSearchForm

    @csrf_protect_m
    @transaction.commit_on_success
    def add_view(self, request, form_url='', extra_context=None):
        "The 'add' admin view for this model."
        model = self.model
        opts = model._meta

        if not self.has_add_permission(request):
            raise PermissionDenied

        form = SavedSearchForm(user=request.user)
        if request.method == 'POST':
            form = SavedSearchForm(data=request.POST, user=request.user)
            if form.is_valid():
                new_object = self.save_form(request, form, change=False)
                form.save()
                form.cleaned_data['group'] = [s.group for s in
                                              form.cleaned_data['site']]
                form.save_m2m()
                self.log_addition(request, new_object)
                return self.response_add(request, new_object)
            else:
                form_validated = False
                new_object = form
                
        else:
            # Prepare the dict of initial data from the request.
            # We have to special-case M2Ms as a list of comma-separated PKs.
            initial = dict(request.GET.items())
            for k in initial:
                try:
                    f = opts.get_field(k)
                except models.FieldDoesNotExist:
                    continue
                if isinstance(f, models.ManyToManyField):
                    initial[k] = initial[k].split(",")

        adminForm = helpers.AdminForm(form, list(self.get_fieldsets(request)),
                                      self.prepopulated_fields,
                                      self.get_readonly_fields(request),
                                      model_admin=self)
        media = self.media + adminForm.media
        context = {
            'title': _('Add %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'is_popup': request.REQUEST.has_key('_popup'),
            'show_delete': False,
            'media': mark_safe(media),
            'inline_admin_formsets': [],
            'errors': helpers.AdminErrorList(form, []),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, form_url=form_url,
                                       add=True)
        
    @csrf_protect_m
    @transaction.commit_on_success
    def change_view(self, request, object_id, extra_context=None):
        "The 'change' admin view for this model."
        model = self.model
        opts = model._meta
        obj = self.get_object(request, unquote(object_id))
        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not'
                            ' exist.') %
                          {'name': force_unicode(opts.verbose_name),
                           'key': escape(object_id)})

        if request.method == 'POST' and request.POST.has_key("_saveasnew"):
            return self.add_view(request, form_url='../add/')

        form = SavedSearchForm(user=request.user, instance=obj)
        if request.method == 'POST':
            form = SavedSearchForm(data=request.POST, user=request.user,
                                   instance=obj)
            if form.is_valid():
                form_validated = True
                # Store the saved but uncommitted form
                new_object = self.save_form(request, form, change=True)
            else:
                form_validated = False
                new_object = obj

            if form_validated:
                form.save()
                form.save_m2m()
                change_message = self.construct_change_message(request, form, [])
                self.log_change(request, new_object, change_message)
                return self.response_change(request, new_object)

        adminForm = helpers.AdminForm(form, self.get_fieldsets(request, obj),
            self.prepopulated_fields, self.get_readonly_fields(request, obj),
            model_admin=self)
        media = self.media + adminForm.media

        context = {
            'title': _('Change %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'object_id': object_id,
            'original': obj,
            'is_popup': request.REQUEST.has_key('_popup'),
            'media': mark_safe(media),
            'inline_admin_formsets': [],
            'errors': helpers.AdminErrorList(form, []),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, change=True, obj=obj)

    def queryset(self, request):
        qs = super(SavedSearchAdmin, self).queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(group__in=request.user.groups.all())

        return qs

    def results(self, obj):
        cache_key = 'savedsearch_count:%s' % obj.id
        results_count = cache.get(cache_key)
        if not results_count:
            results_count = obj.get_sqs().count()
            cache.set(cache_key, results_count, 600)
        return results_count
    results.short_description = 'Results Count'
        
    def last_updated(self, obj):
        return str(obj.date_created)
    last_updated.short_description = 'Last Updated'

    def _make_qs(self, field, params):
        """
        Generates the query string which will be passed to Solr directly.
        
        """
        # If no parameter was passed in, immediately dump back out.
        if not params:
            return ''
        qs = []
        # All fields except full-text search, i.e. keyword search, are
        # sought disjunctively. In other words, if user wants all jobs
        # in Austin, Dallas and San Antonio, we want to search for all
        # jobs in Austin OR Dallas OR San Antonio. Otherwise, searching
        # conjunctively (AND) will result in only those jobs available
        # in ALL of those cities together. The difference between spoken
        # English and logical syntax.
        joinstring = ' OR '
        if field == 'text':
            joinstring = ' AND '
            
        for thing in params:
            if field in ('title', 'text'):
                qs.append('%s:%s' % (field, thing))
            else:
                qs.append('%s:%s' % (field, thing.name))

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


admin.site.register(SavedSearch, SavedSearchAdmin)

