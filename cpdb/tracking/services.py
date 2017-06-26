from models import SearchTracking


class QueryTrackingService(object):
    @staticmethod
    def _count_result(results):
        if results is None:
            return 0

        count = 0
        for _, value in results.iteritems():
            count = count + len(value)

        return count

    @staticmethod
    def execute(term, content_type=None, results={}):
        query_searches = SearchTracking.objects.filter(query=term)
        if len(query_searches) == 0:
            SearchTracking.objects.create(
                query=term, usages=1, results=QueryTrackingService._count_result(results), query_type='free_text'
            )
        else:
            query_search = query_searches[0]
            query_search.usages = query_search.usages + 1
            query_search.results = QueryTrackingService._count_result(results)
            query_search.query_type = 'free_text'
            query_search.save()
