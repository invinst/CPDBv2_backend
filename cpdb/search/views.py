from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import list_route

from search.formatters import AreaFormatter
from .services import SearchManager
from .pagination import SearchQueryPagination
from .formatters import (
    OfficerFormatter, UnitFormatter, OfficerV2Formatter, NameV2Formatter, ReportFormatter, CrFormatter, RankFormatter,
    TRRFormatter
)
from .workers import (
    OfficerWorker, UnitWorker, CommunityWorker, NeighborhoodsWorker, ReportWorker,
    TRRWorker, UnitOfficerWorker, CrWorker, BeatWorker, PoliceDistrictWorker, WardWorker, SchoolGroundWorker, RankWorker
)
from analytics.search_hooks import QueryTrackingSearchHook


class SearchViewSet(viewsets.ViewSet):
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

    @list_route(methods=['get'], url_path='single')
    def single(self, request):
        term = self._search_term
        if not self._content_type:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        query = self.search_manager.get_search_query_for_type(
            term, content_type=self._content_type
        )
        paginator = SearchQueryPagination()
        paginated_query = paginator.paginate_es_query(query, request)
        return paginator.get_paginated_response(
            self.search_manager.get_formatted_results(paginated_query, self._content_type)
        )

    def list(self, request):
        term = self._search_term
        print term
        if term:
            results = self.search_manager.search(term, content_type=self._content_type)
        else:
            results = SearchManager(formatters=self.formatters, workers=self.workers).suggest_sample()

        return Response(results)

    @property
    def _content_type(self):
        return self.request.query_params.get('contentType', None)

    @property
    def _search_term(self):
        return self.request.query_params.get('term', None)


class SearchV1ViewSet(SearchViewSet):
    formatters = {
        'OFFICER': OfficerFormatter,
        'UNIT': UnitFormatter,
        'COMMUNITY': AreaFormatter,
        'NEIGHBORHOOD': AreaFormatter,
        'POLICE-DISTRICT': AreaFormatter,
        'SCHOOL-GROUND': AreaFormatter,
        'WARD': AreaFormatter,
        'BEAT': AreaFormatter,
        'UNIT > OFFICERS': OfficerFormatter,
        'CR': CrFormatter,
        'RANK': RankFormatter,
        'TRR': TRRFormatter,
    }
    workers = {
        'OFFICER': OfficerWorker(),
        'UNIT': UnitWorker(),
        'COMMUNITY': CommunityWorker(),
        'NEIGHBORHOOD': NeighborhoodsWorker(),
        'POLICE-DISTRICT': PoliceDistrictWorker(),
        'SCHOOL-GROUND': SchoolGroundWorker(),
        'WARD': WardWorker(),
        'BEAT': BeatWorker(),
        'UNIT > OFFICERS': UnitOfficerWorker(),
        'CR': CrWorker(),
        'RANK': RankWorker(),
        'TRR': TRRWorker(),
    }


class SearchV2ViewSet(SearchViewSet):
    formatters = {
        'OFFICER': OfficerV2Formatter,
        'UNIT': NameV2Formatter,
        'NEIGHBORHOOD': NameV2Formatter,
        'COMMUNITY': NameV2Formatter,
        'REPORT': ReportFormatter
    }
    workers = {
        'OFFICER': OfficerWorker(),
        'UNIT': UnitWorker(),
        'COMMUNITY': CommunityWorker(),
        'NEIGHBORHOOD': NeighborhoodsWorker(),
        'REPORT': ReportWorker()
    }
