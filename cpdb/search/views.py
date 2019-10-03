from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from search.queries import OfficerQuery, CrQuery, TrrQuery
from search.formatters import AreaFormatter, ZipCodeFormatter
from search.serializers import OfficerSerializer, AllegationSerializer, TRRSerializer
from search.workers import ZipCodeWorker, DateOfficerWorker
from .services import SearchManager
from .pagination import SearchQueryPagination
from .formatters import (
    OfficerFormatter, UnitFormatter, OfficerV2Formatter, NameV2Formatter, RankFormatter,
    ReportFormatter, CRFormatter, TRRFormatter, SearchTermFormatter
)
from .workers import (
    DateCRWorker, DateTRRWorker, OfficerWorker, UnitWorker, CommunityWorker, NeighborhoodsWorker, ReportWorker,
    TRRWorker, UnitOfficerWorker, CRWorker, BeatWorker, PoliceDistrictWorker, WardWorker, SchoolGroundWorker,
    RankWorker, SearchTermItemWorker, InvestigatorCRWorker
)
from analytics.search_hooks import QueryTrackingSearchHook


class SearchViewSet(viewsets.ViewSet):
    formatters = {}
    workers = {}
    hooks = [
        QueryTrackingSearchHook
    ]

    recent_items_queries = []

    def __init__(self, *args, **kwargs):
        super(SearchViewSet, self).__init__(*args, **kwargs)
        self.search_manager = SearchManager(
            formatters=self.formatters,
            workers=self.workers,
            hooks=self.hooks
        )

    @action(detail=False, methods=['get'], url_path='single')
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

    @action(detail=False, methods=['GET'], url_path='recent-search-items', url_name='recent-search-items')
    def recent_search_items(self, _):
        recent_search_data = []
        for recent_items_query in self.recent_items_queries:
            ids = self.request.query_params.getlist(f'{recent_items_query["query_param"]}[]', None)
            if ids:
                items = recent_items_query['query'](ids).query()
                recent_search_data += recent_items_query['serializer'](items, many=True).data

        return Response(
            status=status.HTTP_200_OK,
            data=recent_search_data
        )


class SearchV1ViewSet(SearchViewSet):
    formatters = {
        'SEARCH-TERMS': SearchTermFormatter,
        'DATE > CR': CRFormatter,
        'DATE > TRR': TRRFormatter,
        'DATE > OFFICERS': OfficerFormatter,
        'OFFICER': OfficerFormatter,
        'UNIT': UnitFormatter,
        'COMMUNITY': AreaFormatter,
        'NEIGHBORHOOD': AreaFormatter,
        'POLICE-DISTRICT': AreaFormatter,
        'SCHOOL-GROUND': AreaFormatter,
        'WARD': AreaFormatter,
        'BEAT': AreaFormatter,
        'UNIT > OFFICERS': OfficerFormatter,
        'CR': CRFormatter,
        'RANK': RankFormatter,
        'TRR': TRRFormatter,
        'ZIP-CODE': ZipCodeFormatter,
        'INVESTIGATOR > CR': CRFormatter,
    }
    workers = {
        'SEARCH-TERMS': SearchTermItemWorker(),
        'DATE > CR': DateCRWorker(),
        'DATE > TRR': DateTRRWorker(),
        'DATE > OFFICERS': DateOfficerWorker(),
        'OFFICER': OfficerWorker(),
        'UNIT': UnitWorker(),
        'COMMUNITY': CommunityWorker(),
        'NEIGHBORHOOD': NeighborhoodsWorker(),
        'POLICE-DISTRICT': PoliceDistrictWorker(),
        'SCHOOL-GROUND': SchoolGroundWorker(),
        'WARD': WardWorker(),
        'BEAT': BeatWorker(),
        'UNIT > OFFICERS': UnitOfficerWorker(),
        'CR': CRWorker(),
        'RANK': RankWorker(),
        'TRR': TRRWorker(),
        'ZIP-CODE': ZipCodeWorker(),
        'INVESTIGATOR > CR': InvestigatorCRWorker(),
    }

    recent_items_queries = [
        {
            'query_param': 'officer_ids',
            'query': OfficerQuery,
            'serializer': OfficerSerializer,
        },
        {
            'query_param': 'crids',
            'query': CrQuery,
            'serializer': AllegationSerializer,
        },
        {
            'query_param': 'trr_ids',
            'query': TrrQuery,
            'serializer': TRRSerializer,
        },
    ]


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
