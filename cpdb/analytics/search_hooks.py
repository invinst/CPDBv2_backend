from .models import SearchTracking


class QueryTrackingSearchHook(object):
    @staticmethod
    def _count_result(results):
        results = results or {}
        return sum(len(value) for _, value in results.items())

    @staticmethod
    def execute(term, content_type=None, results={}):
        query_searches = SearchTracking.objects.filter(query=term)
        if len(query_searches) == 0:
            SearchTracking.objects.create(
                query=term, usages=1, results=QueryTrackingSearchHook._count_result(results), query_type='free_text'
            )
        else:
            query_search = query_searches[0]
            query_search.usages = query_search.usages + 1
            query_search.results = QueryTrackingSearchHook._count_result(results)
            query_search.query_type = 'free_text'
            query_search.save()
