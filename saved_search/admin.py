from django import forms
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.util import unquote
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import transaction, models
from django.forms.formsets import all_valid
from django.http import Http404
from django.utils.encoding import force_unicode
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect

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
        groups = [g.id for g in user.groups.all()]
        qs = Group.objects.filter(id__in=groups)
        if 'group' not in self.fields:
            # If the form instance doesn't have the group field, create it
            # with our dynamic querystring.
            self.fields['group'] = forms.ModelMultipleChoiceField(queryset=qs)
        else:
            # If it does, it will simply set the querystring for the
            # existing field to our dynamic querystring. Otherwise every
            # time it is initialized via __init__ its queryset will be
            # set back to Group.objects.all() which is undesired behavior.
            self.fields['group'].queryset = qs

    class Meta:
        model = SavedSearch
        exclude = ("name_slug", "city", "state", "country",
                   "querystring")


class SavedSearchAdmin(admin.ModelAdmin):
    search_fields = ['country__name', 'state__name', 'city__name', 'keyword',
                     'title']

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

        ModelForm = SavedSearchForm(user=request.user)
        formsets = []
        if request.method == 'POST':
            form = SavedSearchForm(data=request.POST, user=request.user)
            if form.is_valid():
                new_object = self.save_form(request, form, change=False)
                form_validated = True
            else:
                form_validated = False
                new_object = SavedSearchForm
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request),
                                       self.inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(data=request.POST, files=request.FILES,
                                  instance=new_object,
                                  save_as_new=request.POST.has_key("_saveasnew"),
                                  prefix=prefix,
                                  queryset=inline.queryset(request))
                formsets.append(formset)
            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, change=False)
                form.save_m2m()
                for formset in formsets:
                    self.save_formset(request, form, formset, change=False)

                self.log_addition(request, new_object)
                return self.response_add(request, new_object)
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
            form = ModelForm
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request),
                                       self.inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=self.model(), prefix=prefix,
                                  queryset=inline.queryset(request))
                formsets.append(formset)

        adminForm = helpers.AdminForm(form, list(self.get_fieldsets(request)),
            self.prepopulated_fields, self.get_readonly_fields(request),
            model_admin=self)
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(self.inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request))
            readonly = list(inline.get_readonly_fields(request))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
                fieldsets, readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context = {
            'title': _('Add %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'is_popup': request.REQUEST.has_key('_popup'),
            'show_delete': False,
            'media': mark_safe(media),
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, form_url=form_url,
                                       add=True)
        
    @csrf_protect_m
    @transaction.commit_on_success
    def change_view(self, request, object_id, extra_context=None):
        import ipdb
        ipdb.set_trace()
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

        ModelForm = SavedSearchForm(user=request.user, instance=obj)
        if request.method == 'POST':
            form = SavedSearchForm(data=request.POST, user=request.user,
                                   instance=obj)
            if form.is_valid():
                form_validated = True
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
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, change=True, obj=obj)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'group':
            groups = request.user.groups.all()
            kwargs['queryset'] = Group.objects.filter(id__in=groups)
        return super(SavedSearchAdmin, self).formfield_for_manytomany(db_field,
                                                                      request,
                                                                      **kwargs)

    def queryset(self, request):
        qs = super(SavedSearchAdmin, self).queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(group__in=request.user.groups.all())

        return qs
            
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
