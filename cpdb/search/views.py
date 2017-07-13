from rest_framework import viewsets
from rest_framework.response import Response

from .services import SearchManager
from .formatters import (
    OfficerFormatter, NameFormatter, OfficerV2Formatter, NameV2Formatter,
    FAQFormatter, ReportFormatter)
from .workers import (
    OfficerWorker, UnitWorker, CommunityWorker, NeighborhoodsWorker, FAQWorker, ReportWorker,
    CoAccusedOfficerWorker, UnitOfficerWorker)
from analytics.search_hooks import QueryTrackingSearchHook


class SearchViewSet(viewsets.ViewSet):
    lookup_field = 'text'
    formatters = {}
    workers = {}
    hooks = [
        QueryTrackingSearchHook
    ]

    def retrieve(self, request, text):
        results = SearchManager(
            formatters=self.formatters,
            workers=self.workers,
            hooks=self.hooks
        ).search(
            text,
            content_type=self._content_type
        )

        return Response(results)

    def list(self, request):
        results = SearchManager(
            formatters=self.formatters,
            workers=self.workers
        ).suggest_sample()

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
        'COMMUNITY': NameFormatter,
        'CO-ACCUSED': OfficerFormatter,
        'UNIT > OFFICERS': OfficerFormatter
    }
    workers = {
        'OFFICER': OfficerWorker(),
        'UNIT': UnitWorker(),
        'COMMUNITY': CommunityWorker(),
        'NEIGHBORHOOD': NeighborhoodsWorker(),
        'CO-ACCUSED': CoAccusedOfficerWorker(),
        'UNIT > OFFICERS': UnitOfficerWorker()
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
