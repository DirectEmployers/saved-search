from django.conf import settings
from django.utils import tree

from haystack.backends import log_query, EmptyResults, BaseEngine, SearchNode
from haystack.backends.solr_backend import SolrSearchBackend, SolrSearchQuery
from haystack.constants import ID, DJANGO_CT, DJANGO_ID
from haystack.models import SearchResult
from haystack.query import SearchQuerySet, SQ

from pysolr import SolrError


class GroupQuerySet(SearchQuerySet):
    def group_query(self, *args, **kwargs):
        """
        Performs a group query against a standard query.
        Works in the same manner as .filter().
        
        """
        clone = self._clone()
        clone.query.add_group_query(*args, **kwargs)
        return clone

    def __len__(self):
        if not self.query._results:
            qc = self.query.get_count()
            
        return len(self.query._results)


class GroupQueryError(Exception):
    def __init__(self, value):
        self.param = value

    def __str__(self):
        return repr(self.param)
    
    
class SolrGroupSearchBackend(SolrSearchBackend):
    """
    Solr's result grouping feature is very useful but provides results of
    a different structure than standard "vanilla" queries that pysolr &
    Haystack are oriented toward. This backend, in conjunction with my
    fork of pysolr, the SolrGroupSearchQuery and GroupQuerySet, provides
    compatibility with results of this nature.

    http://wiki.apache.org/solr/FieldCollapsing
    
    """
    @log_query
    def search(self, query_string, sort_by=None, start_offset=0, end_offset=None,
               fields='', highlight=False, facets=None, date_facets=None,
               query_facets=None, narrow_queries=None, spelling_query=None,
               limit_to_registered_models=None, result_class=None, group=True,
               group_ngroups=True, group_query=[], group_format="simple",
               **kwargs):

        if not group_query:
            raise GroupQueryError("You must specify at least one group query.")
                
        if len(query_string) == 0:
            return {
                'results': [],
                'hits': 0,
            }

        kwargs = {
            'fl': '* score',
            'group': group,
            'group.ngroups': group_ngroups,
            'group.format': group_format,
            'group.query': group_query
        }

        if fields:
            kwargs['fl'] = fields

        if sort_by is not None:
            kwargs['sort'] = sort_by

        if start_offset is None and end_offset is None:
            kwargs['rows'] = 1
        elif start_offset is not None:
            kwargs['start'] = start_offset
        elif end_offset is not None:
            kwargs['rows'] = end_offset - start_offset

        if highlight is True:
            kwargs['hl'] = 'true'
            kwargs['hl.fragsize'] = '200'

        if self.include_spelling is True:
            kwargs['spellcheck'] = 'true'
            kwargs['spellcheck.collate'] = 'true'
            kwargs['spellcheck.count'] = 1

            if spelling_query:
                kwargs['spellcheck.q'] = spelling_query

        if facets is not None:
            kwargs['facet'] = 'on'
            kwargs['facet.field'] = facets.keys()

            for facet_field, options in facets.items():
                for key, value in options.items():
                    kwargs['f.%s.facet.%s' % (facet_field, key)] = self.conn._from_python(value)


        kwargs['group'] = self.conn._from_python(kwargs['group'])
        kwargs['group.ngroups'] = self.conn._from_python(kwargs['group.ngroups'])

        if date_facets is not None:
            kwargs['facet'] = 'on'
            kwargs['facet.date'] = date_facets.keys()
            kwargs['facet.date.other'] = 'none'

            for key, value in date_facets.items():
                kwargs["f.%s.facet.date.start" % key] = self.conn._from_python(
                    value.get('start_date'))
                kwargs["f.%s.facet.date.end" % key] = self.conn._from_python(
                    value.get('end_date'))
                gap_by_string = value.get('gap_by').upper()
                gap_string = "%d%s" % (value.get('gap_amount'), gap_by_string)

                if value.get('gap_amount') != 1:
                    gap_string += "S"

                kwargs["f.%s.facet.date.gap" % key] = '+%s/%s' % (gap_string,
                                                                  gap_by_string)

        if query_facets is not None:
            kwargs['facet'] = 'on'
            kwargs['facet.query'] = ["%s:%s" % (field, value) for field, value
                                     in query_facets]

        if limit_to_registered_models is None:
            lrm = 'HAYSTACK_LIMIT_TO_REGISTERED_MODELS'
            limit_to_registered_models = getattr(settings, lrm, True)

        if limit_to_registered_models:
            # Using narrow queries, limit the results to only models handled
            # with the current routers.
            if narrow_queries is None:
                narrow_queries = set()

            registered_models = self.build_models_list()

            if len(registered_models) > 0:
                narrow_queries.add('%s:(%s)' % (DJANGO_CT,
                                                ' OR '.join(registered_models)))

        if narrow_queries is not None:
            kwargs['fq'] = list(narrow_queries)

        try:
            raw_results = self.conn.search(query_string, **kwargs)
        except (IOError, SolrError) as e:
            if not self.silently_fail:
                raise

            self.log.error("Failed to query Solr using '%s': %s", query_string,
                           e)
            raw_results = [EmptyResults()]

        if hasattr(raw_results, 'grouped'):
            return [self._process_results(res, highlight=highlight,
                                          result_class=result_class)
                    for res in raw_results.grouped.iteritems()]
        else:
            return []

    def _process_results(self, raw_results, highlight=False, result_class=None):
        from haystack import connections

        results = []
        try:
            hits = raw_results[1]['doclist']['numFound']
        except (KeyError, IndexError):
            hits = 0

        try:
            group = raw_results[0]
        except IndexError:
            group = ""

        facets = {}
        spelling_suggestion = None

        if result_class is None:
            result_class = SearchResult

        if hasattr(raw_results, 'facets'):
            facets = {
                'fields': raw_results.facets.get('facet_fields', {}),
                'dates': raw_results.facets.get('facet_dates', {}),
                'queries': raw_results.facets.get('facet_queries', {}),
            }

            for key in ['fields']:
                for facet_field in facets[key]:
                    # Convert to a two-tuple, as Solr's json format returns a list of
                    # pairs.
                    facets[key][facet_field] = zip(facets[key][facet_field][::2],
                                                   facets[key][facet_field][1::2])

        if self.include_spelling is True:
            if hasattr(raw_results, 'spellcheck'):
                if len(raw_results.spellcheck.get('suggestions', [])):
                    # For some reason, it's an array of pairs. Pull off the
                    # collated result from the end.
                    spelling_suggestion = raw_results.spellcheck.get('suggestions')[-1]

        return {
            'group': group,
            'results': results,
            'hits': hits,
            'facets': facets,
            'spelling_suggestion': spelling_suggestion
        }

class SolrGroupSearchQuery(SolrSearchQuery):
    def __init__(self, **kwargs):
        super(SolrGroupSearchQuery, self).__init__(**kwargs)
        self.group = True
        self.gquery_filter = SearchNode()
        self.group_format = "simple"
        self.group_ngroups = True
        self.group_queries = set()

    def add_group_query(self, query_filter, use_or=False, is_master=True,
                        tag=None):
        """
        Adds a group query to the current query.
        """
        if use_or:
            connector = SQ.OR
        else:
            connector = SQ.AND

        if self.gquery_filter and query_filter.connector != SQ.AND and len(query_filter) > 1:
            self.gquery_filter.start_subtree(connector)
            subtree = True
        else:
            subtree = False

        for child in query_filter.children:
            if isinstance(child, tree.Node):
                self.gquery_filter.start_subtree(connector)
                self.add_group_query(child, is_master=False)
                self.gquery_filter.end_subtree()
            else:
                expression, value = child
                self.gquery_filter.add((expression, value), connector)

            connector = query_filter.connector

        if query_filter.negated:
            self.gquery_filter.negate()

        if subtree:
            self.gquery_filter.end_subtree()

        if is_master:
            # If and only if we have iterated through all the children of the
            # query_filter, the SQ object, append the query fragment to the
            # set of group queries, and reset self.gquery_filter back to an
            # empty SearchNode.
            qfrag = self.gquery_filter.as_query_string(self.build_query_fragment)

            # If specified, add a local param to identify individual group
            # query statements.
            if tag:
                qfrag = '{!tag="%s"} ' % str(tag) + qfrag
            
            if qfrag:
                self.group_queries.add(qfrag)

            self.gquery_filter = SearchNode()
            
    def run(self, spelling_query=None, **kwargs):
        """Builds & executes the query. Returns a list of result groupings."""
        final_query = self.build_query()

        kwargs['start_offset'] = self.start_offset
        kwargs['result_class'] = self.result_class
        kwargs['group_query'] = [i for i in self.group_queries]
        kwargs['group_format'] = self.group_format
        kwargs['group_ngroups'] = self.group_ngroups

        if self.order_by:
            order_by_list = []

            for order_by in self.order_by:
                if order_by.startswith('-'):
                    order_by_list.append('%s desc' % order_by[1:])
                else:
                    order_by_list.append('%s asc' % order_by)

            kwargs['sort_by'] = ", ".join(order_by_list)

        if self.narrow_queries:
            kwargs['narrow_queries'] = self.narrow_queries

        if self.query_facets:
            kwargs['query_facets'] = self.query_facets

        if self.end_offset is not None:
            kwargs['end_offset'] = self.end_offset

        if self.highlight:
            kwargs['highlight'] = self.highlight

        if spelling_query:
            kwargs['spelling_query'] = spelling_query

        self._results = self.backend.search(final_query, **kwargs)
        self._hit_count = sum([r['hits'] for r in self._results])

    def has_run(self):
        """Indicates if any query has been run."""
        return None not in (self._results, self._hit_count)

    def _clone(self, **kwargs):
        clone = super(SolrGroupSearchQuery, self)._clone(**kwargs)
        clone.group_queries = self.group_queries
        return clone
        

class SolrGrpEngine(BaseEngine):
    backend = SolrGroupSearchBackend
    query = SolrGroupSearchQuery
