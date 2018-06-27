from search.workers import OfficerWorker
from search.views import SearchViewSet
from .formatters import OfficerV2Formatter


class SearchMobileV2ViewSet(SearchViewSet):
    lookup_field = 'text'

    formatters = {
        'OFFICER': OfficerV2Formatter,
    }

    workers = {
        'OFFICER': OfficerWorker()
    }
