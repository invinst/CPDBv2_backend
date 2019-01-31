from search.workers import OfficerWorker, TRRWorker, CRWorker, DateCRWorker, DateTRRWorker, DateOfficerWorker, \
    InvestigatorCRWorker
from search.views import SearchViewSet
from .formatters import OfficerV2Formatter, CRFormatter, TRRFormatter


class SearchMobileV2ViewSet(SearchViewSet):
    lookup_field = 'text'

    formatters = {
        'DATE > CR': CRFormatter,
        'DATE > TRR': TRRFormatter,
        'DATE > OFFICERS': OfficerV2Formatter,
        'OFFICER': OfficerV2Formatter,
        'CR': CRFormatter,
        'TRR': TRRFormatter,
        'INVESTIGATOR > CR': CRFormatter,
    }

    workers = {
        'DATE > CR': DateCRWorker(),
        'DATE > TRR': DateTRRWorker(),
        'OFFICER': OfficerWorker(),
        'CR': CRWorker(),
        'TRR': TRRWorker(),
        'DATE > OFFICERS': DateOfficerWorker(),
        'INVESTIGATOR > CR': InvestigatorCRWorker(),
    }
