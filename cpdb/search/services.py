from search.date_util import find_dates_from_string
from search.workers import (
    DateWorker,
    OfficerWorker,
    UnitWorker,
    CommunityWorker,
    NeighborhoodsWorker
)
from .formatters import SimpleFormatter


DEFAULT_SEARCH_WORKERS = {
    'OFFICER': OfficerWorker(),
    'UNIT': UnitWorker(),
    'COMMUNITY': CommunityWorker(),
    'NEIGHBORHOOD': NeighborhoodsWorker()
}


class SearchManager(object):
    def __init__(self, formatters=None, workers=None, hooks=None):
        self.formatters = formatters or {}
        self.workers = workers or DEFAULT_SEARCH_WORKERS
        self.hooks = hooks or []

    def search(self, term, content_type=None, limit=10):
        response = {}

        _workers = {content_type: self.workers[content_type]} if content_type else self.workers
        search_with_dates = any([isinstance(worker, DateWorker) for worker in _workers.values()])
        dates = [date.strftime('%Y-%m-%d') for date in find_dates_from_string(term)] if search_with_dates else []

        for _content_type, worker in _workers.items():
            search_results = worker.search(term, size=limit, dates=dates)
            response[_content_type] = self._formatter_for(_content_type)().format(search_results)

        for hook in self.hooks:
            hook.execute(term, content_type, response)

        return response

    def get_search_query_for_type(self, term, content_type):
        worker = self.workers[content_type]
        dates = [
            date.strftime('%Y-%m-%d') for date in find_dates_from_string(term)
        ] if isinstance(worker, DateWorker) else []
        return worker.query(term, dates=dates)

    def get_formatted_results(self, documents, content_type):
        return self._formatter_for(content_type)().serialize(documents)

    def suggest_sample(self):
        '''
        Return 1 random item that has tags from each content type.
        '''
        response = {}

        for content_type, worker in self.workers.items():
            search_results = worker.get_sample()
            response[content_type] = self._formatter_for(content_type)().format(search_results)

        return response

    def _formatter_for(self, content_type):
        return self.formatters.get(content_type, SimpleFormatter)
