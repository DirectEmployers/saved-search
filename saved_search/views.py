from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http import Http404
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic import ListView

from haystack.query import SearchQuerySet

from saved_search.forms import SavedSearchForm, LoginForm
from saved_search.models import SavedSearch


class SavedSearchListView(ListView):
    context_object_name = "svd_searches"
    template_name = "userhome.html"
    paginate_by = 50
    
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        if user.is_superuser:
            return SavedSearch.objects.all()
        else:
            groups = user.groups.all()
            return SavedSearch.objects.filter(group__in=group)
    

@login_required(login_url="/saved-search/login/")
def saved_search_view(request, username, svdsrch_id=None):
    if request.user.username != username:
        if request.user.is_superuser:
            return redirect('/saved-search/%s/%s' % (request.user.username,
                                                     svdsrch_id))
        else:
            raise Http404
            
    user = get_object_or_404(User, username=username)
    
    if svdsrch_id == None:
        form = SavedSearchForm(user=user)
    else:
        item = get_object_or_404(SavedSearch, id=svdsrch_id)
        form = SavedSearchForm(user=user, instance=item)
        
    if request.method == 'POST':
        form = SavedSearchForm(request.POST, user=user)
        if form.is_valid():
            _update_tags(item, form)
            form.save()
            messages.success(request,
                             "Your Saved Search was created :D")
            return redirect('/saved-search/%s' % request.user)
    return render_to_response("savedsearchform.html", {"form": form},
                              context_instance=RequestContext(request))

def login(request):
    form = LoginForm()
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('/saved-search')
            else:
                messages.error(request, "You do not have proper permissions to "
                               "use this application. Ensure you are logging in"
                               " using your application's admin user/pass.")
        else:
            messages.error(request, "Invalid username or password. Ensure y"
                           "ou are logging in using your application's admi"
                           "n user/pass.", fail_silently=True)

    return render_to_response('/saved-search/login.html', {'form': form},
                              context_instance=RequestContext(request))

def _update_tags(item, form):
    """Update taggit tags for a given SavedSearch instance."""
    itemset = set(item.keyword.all())
    tagstringset = set(form.cleaned_data['keyword'])
    for tag in itemset.difference(tagstringset):
        item.keyword.remove(tag)
    for tag in tagstringset.difference(itemset):
        item.keyword.add(tag)
    return item

def _location_data(request):
    """
    Convert Solr facet counts to JSON object for consumption by location
    dialogue when creating/editing Saved Searches.
    
    """
    results = {}
    sqs = SearchQuerySet().facet("full_loc")
    locs = sqs.facet_counts()['fields']['full_loc']
    for loc in locs:
        loc_tuples = loc[0].split('@@')
        for atom in loc_tuples:
            loc_tuples[loc_tuples.index(atom)] = atom.split('::')
        locs[locs.index(loc)] = dict(loc_tuples)
    # `locs` now looks like:
    #
    # [{'city': 'Topeka',
    #   'country': 'United States',
    #   'location': 'Topeka, KS',
    #   'state': 'Kansas'},
    #  {'city': 'Indianapolis',
    #   'country': 'United States',
    #   'location': 'Indianapolis, IN',
    #   'state': 'Indiana'},
    #   ...
    #   etc.]
            
            
            
        
