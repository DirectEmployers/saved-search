from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.util import unquote
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db import transaction, models
from django.http import Http404
from django.utils.encoding import force_unicode
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect

from saved_search.forms import SavedSearchForm
from saved_search.models import SavedSearch

csrf_protect_m = method_decorator(csrf_protect)


class SavedSearchAdmin(admin.ModelAdmin):
    search_fields = ['country', 'state', 'city', 'title',
                     'site__name']
    list_display = ('name', 'last_updated')
    list_filter = ('group',)
    save_as = True

    def get_form(self, request, obj=None, **kwargs):
        return SavedSearchForm

    @csrf_protect_m
    @transaction.commit_on_success
    def add_view(self, request, form_url='', extra_context=None):
        """The 'add' admin view for this model."""
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
                form.cleaned_data['group'] = [form.cleaned_data['site'].group]
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
                # This is kind of heinous. Need some UI magic here to make this
                # not awful.
                form.cleaned_data['keyword'] = form._keywords + form.cleaned_data['new_keyword']
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

    # def queryset(self, request):
    #     qs = super(SavedSearchAdmin, self).queryset(request)
    #     if not request.user.is_superuser:
    #         qs = qs.filter(group__in=request.user.groups.all())

    #     return qs

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


admin.site.register(SavedSearch, SavedSearchAdmin)

