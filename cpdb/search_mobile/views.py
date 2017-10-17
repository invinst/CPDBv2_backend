from search.workers import OfficerWorker, FAQWorker, ReportWorker, UnitWorker
from search.views import SearchViewSet
from .formatters import OfficerV2Formatter, FAQFormatter, ReportFormatter, UnitFormatter


class SearchMobileV2ViewSet(SearchViewSet):
    lookup_field = 'text'

    formatters = {
        'OFFICER': OfficerV2Formatter,
        'FAQ': FAQFormatter,
        'REPORT': ReportFormatter,
        'UNIT': UnitFormatter
    }

    workers = {
        'OFFICER': OfficerWorker(),
        'FAQ': FAQWorker(),
        'REPORT': ReportWorker(),
        'UNIT': UnitWorker()
    }
