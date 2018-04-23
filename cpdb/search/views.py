from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from search.formatters import AreaFormatter
from .services import SearchManager
from .pagination import SearchQueryPagination
from .formatters import (
    OfficerFormatter, UnitFormatter, OfficerV2Formatter, NameV2Formatter,
    FAQFormatter, ReportFormatter, CrFormatter
)
from .workers import (
    OfficerWorker, UnitWorker, CommunityWorker, NeighborhoodsWorker, FAQWorker, ReportWorker,
    UnitOfficerWorker, CrWorker
)
from analytics.search_hooks import QueryTrackingSearchHook


class SearchViewSet(viewsets.ViewSet):
    lookup_field = 'text'
    formatters = {}
    workers = {}
    hooks = [
        QueryTrackingSearchHook
    ]

    def __init__(self, *args, **kwargs):
        super(SearchViewSet, self).__init__(*args, **kwargs)
        self.search_manager = SearchManager(
            formatters=self.formatters,
            workers=self.workers,
            hooks=self.hooks
        )

    def retrieve(self, request, text):
        results = self.search_manager.search(
            text,
            content_type=self._content_type
        )

        return Response(results)

    @detail_route(methods=['get'], url_path='single')
    def single(self, request, text):
        if not self._content_type:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        query = self.search_manager.get_search_query_for_type(
            text, content_type=self._content_type
        )
        paginator = SearchQueryPagination()
        paginated_query = paginator.paginate_es_query(query, request)
        return paginator.get_paginated_response(
            self.search_manager.get_formatted_results(paginated_query, self._content_type)
        )

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
        'UNIT': UnitFormatter,
        'NEIGHBORHOOD': AreaFormatter,
        'COMMUNITY': AreaFormatter,
        'UNIT > OFFICERS': OfficerFormatter,
        'CR': CrFormatter
    }
    workers = {
        'OFFICER': OfficerWorker(),
        'UNIT': UnitWorker(),
        'COMMUNITY': CommunityWorker(),
        'NEIGHBORHOOD': NeighborhoodsWorker(),
        'UNIT > OFFICERS': UnitOfficerWorker(),
        'CR': CrWorker()
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
