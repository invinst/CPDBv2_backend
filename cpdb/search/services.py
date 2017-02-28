from .workers import (
    OfficerWorker, UnitWorker, CommunityWorker, NeighborhoodsWorker)
from .formatters import SimpleFormatter


DEFAULT_SEARCH_WORKERS = {
    'OFFICER': OfficerWorker(),
    'UNIT': UnitWorker(),
    'COMMUNITY': CommunityWorker(),
    'NEIGHBORHOOD': NeighborhoodsWorker()
}


class SearchManager(object):
    def __init__(self, formatters=None, workers=None):
        self.formatters = formatters or {}
        self.workers = workers or DEFAULT_SEARCH_WORKERS

    def search(self, term, content_type=None, limit=10000):
        response = {}

        if content_type:
            search_results = self.workers[content_type].search(term, size=limit)
            response[content_type] = self._formatter_for(content_type)().format(search_results)

        else:
            for content_type, worker in self.workers.items():
                search_results = worker.search(term)
                response[content_type] = self._formatter_for(content_type)().format(search_results)

        return response

    def suggest_random(self):
        '''
        Return 1 random item for each content type.
        '''
        response = {}

        for content_type, worker in self.workers.items():
            search_results = worker.get_random()
            response[content_type] = self._formatter_for(content_type)().format(search_results)

        return response

    def _formatter_for(self, content_type):
        return self.formatters.get(content_type, SimpleFormatter)
