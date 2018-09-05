from search.workers import OfficerWorker, TRRWorker, CRWorker, DateCRWorker, DateTRRWorker
from search.views import SearchViewSet
from .formatters import OfficerV2Formatter, CRFormatter, TRRFormatter


class SearchMobileV2ViewSet(SearchViewSet):
    lookup_field = 'text'

    formatters = {
        'DATE > CR': CRFormatter,
        'DATE > TRR': TRRFormatter,
        'OFFICER': OfficerV2Formatter,
        'CR': CRFormatter,
        'TRR': TRRFormatter,
    }

    workers = {
        'DATE > CR': DateCRWorker(),
        'DATE > TRR': DateTRRWorker(),
        'OFFICER': OfficerWorker(),
        'CR': CRWorker(),
        'TRR': TRRWorker()
    }
