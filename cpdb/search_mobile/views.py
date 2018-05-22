from search.workers import OfficerWorker, ReportWorker, UnitWorker
from search.views import SearchViewSet
from .formatters import OfficerV2Formatter, ReportFormatter, UnitFormatter


class SearchMobileV2ViewSet(SearchViewSet):
    lookup_field = 'text'

    formatters = {
        'OFFICER': OfficerV2Formatter,
        'REPORT': ReportFormatter,
        'UNIT': UnitFormatter
    }

    workers = {
        'OFFICER': OfficerWorker(),
        'REPORT': ReportWorker(),
        'UNIT': UnitWorker()
    }
