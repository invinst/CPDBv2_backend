from rest_framework import viewsets
from rest_framework.response import Response

from .services import SearchManager
from .formatters import (
    OfficerFormatter, NameFormatter, OfficerV2Formatter, NameV2Formatter,
    FAQFormatter, ReportFormatter)
from .workers import (
    OfficerWorker, UnitWorker, CommunityWorker, NeighborhoodsWorker, FAQWorker, ReportWorker)


class SearchViewSet(viewsets.ViewSet):
    lookup_field = 'text'
    formatters = {}
    workers = {}

    def retrieve(self, request, text):
        results = SearchManager(formatters=self.formatters, workers=self.workers).search(
            text, content_type=self._content_type)
        return Response(results)

    @property
    def _content_type(self):
        return self.request.query_params.get('contentType', None)


class SearchV1ViewSet(SearchViewSet):
    lookup_field = 'text'
    formatters = {
        'OFFICER': OfficerFormatter,
        'UNIT': NameFormatter,
        'NEIGHBORHOOD': NameFormatter,
        'COMMUNITY': NameFormatter
    }
    workers = {
        'OFFICER': OfficerWorker(),
        'UNIT': UnitWorker(),
        'COMMUNITY': CommunityWorker(),
        'NEIGHBORHOOD': NeighborhoodsWorker()
    }


class SearchV2ViewSet(SearchViewSet):
    lookup_field = 'text'
    formatters = {
        'OFFICER': OfficerV2Formatter,
        'UNIT': NameV2Formatter,
        'NEIGHBORHOOD': NameV2Formatter,
        'COMMUNITY': NameV2Formatter,
        'FAQ': FAQFormatter,
        'REPORT': ReportFormatter
    }
    workers = {
        'OFFICER': OfficerWorker(),
        'UNIT': UnitWorker(),
        'COMMUNITY': CommunityWorker(),
        'NEIGHBORHOOD': NeighborhoodsWorker(),
        'FAQ': FAQWorker(),
        'REPORT': ReportWorker()
    }
