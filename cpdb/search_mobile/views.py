from search.workers import OfficerWorker, TRRWorker, CrWorker
from search.views import SearchViewSet
from .formatters import OfficerV2Formatter, CRFormatter, TRRFormatter


class SearchMobileV2ViewSet(SearchViewSet):
    lookup_field = 'text'

    formatters = {
        'OFFICER': OfficerV2Formatter,
        'CR': CRFormatter,
        'TRR': TRRFormatter
    }

    workers = {
        'OFFICER': OfficerWorker(),
        'CR': CrWorker(),
        'TRR': TRRWorker()
    }
