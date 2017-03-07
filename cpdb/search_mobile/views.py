from search.workers import OfficerWorker, FAQWorker, ReportWorker
from search.views import SearchViewSet
from .formatters import OfficerV2Formatter, FAQFormatter, ReportFormatter


class SearchMobileV2ViewSet(SearchViewSet):
    lookup_field = 'text'

    formatters = {
        'OFFICER': OfficerV2Formatter,
        'FAQ': FAQFormatter,
        'REPORT': ReportFormatter
    }

    workers = {
        'OFFICER': OfficerWorker(),
        'FAQ': FAQWorker(),
        'REPORT': ReportWorker()
    }
