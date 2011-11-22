from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from saved_search.models import SavedSearch
from saved_search.views import SavedSearchListView

urlpatterns = patterns('',
                       url(r'^login/', 'saved_search.views.login', name="login"),
                       url(r'^(?P<username>.*)/(?P<svdsrch_id>[0-9]+)/',
                           'saved_search.views.saved_search_view',
                           name="edit_item"),
                       url(r'^(?P<username>.*)/new-saved-search/',
                           'saved_search.views.saved_search_view',
                           name="add_item"),
                       url(r'^(?P<username>.*)/',
                           login_required(SavedSearchListView.as_view(),
                                          login_url='/saved-search/login/'),
                           name="userhome"),
                   )
