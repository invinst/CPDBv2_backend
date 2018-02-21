from elasticsearch_dsl.query import Q
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route

from activity_grid.serializers import OfficerCardSerializer
from data.models import Officer
from es_index.pagination import ESQueryPagination
from officers.doc_types import OfficerSocialGraphDocType, OfficerPercentileDocType
from officers.serializers import OfficerYearlyPercentileSerializer
from .doc_types import OfficerSummaryDocType, OfficerTimelineEventDocType
from .serializers import TimelineSerializer, TimelineMinimapSerializer

_ALLOWED_FILTERS = [
    'category',
    'race',
    'gender',
    'age',
]


class OfficersViewSet(viewsets.ViewSet):
    @detail_route(methods=['get'])
    def summary(self, request, pk):
        query = OfficerSummaryDocType().search().query('term', id=pk)
        search_result = query.execute()
        try:
            return Response(search_result[0].to_dict())
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def _query_timeline_items(self, request, pk):
        if request.GET.get('sort') == 'asc':
            sort_order = ['year_sort', 'date_sort', 'priority_sort']
        else:
            sort_order = ['-year_sort', '-date_sort', '-priority_sort']
        query = OfficerTimelineEventDocType().search().sort(*sort_order).query('term', officer_id=pk)

        filter_params = []
        for filter in _ALLOWED_FILTERS:
            if filter in request.GET:
                condition = {filter + '__keyword': request.GET[filter]}
                filter_params.append(Q('term', **condition))

        # match all non-CR events and CR events that match provided filters
        if filter_params:
            query = query.filter(~Q('match', kind='CR') | Q('bool', must=filter_params))

        return query

    @detail_route(methods=['get'], url_path='timeline-items')
    def timeline_items(self, request, pk):
        if Officer.objects.filter(pk=pk).exists():
            query = self._query_timeline_items(request, pk)

            paginator = ESQueryPagination()
            paginated_query = paginator.paginate_es_query(query, request)
            serializer = TimelineSerializer(paginated_query, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @detail_route(methods=['get'], url_path='timeline-minimap')
    def timeline_minimap(self, request, pk):
        if Officer.objects.filter(pk=pk).exists():
            query = self._query_timeline_items(request, pk)

            return Response(TimelineMinimapSerializer(query[:10000].execute(), many=True).data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @detail_route(methods=['get'], url_path='social-graph')
    def social_graph(self, request, pk):
        query = OfficerSocialGraphDocType().search().query('term', officer_id=pk)
        search_result = query.execute()
        try:
            return Response(search_result[0].to_dict()['graph'])
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @detail_route(methods=['get'], url_path='percentile')
    def officer_percentile(self, request, pk):
        query = OfficerPercentileDocType().search().query('term', officer_id=pk).sort('year')
        results = query[:100].execute()
        return Response(OfficerYearlyPercentileSerializer(results, many=True).data)

    @list_route(methods=['get'], url_path='top-by-allegation')
    def top_officers_by_allegation(self, request):
        is_random = request.GET.get('random', 0)
        limit = request.GET.get('limit', 48)
        if is_random:
            queryset = Officer.objects.filter(complaint_percentile__gt=99.0).order_by('?')
        else:
            queryset = Officer.objects.filter(complaint_percentile__gt=99.0).order_by('-complaint_percentile')

        limit = min(len(queryset), limit)
        queryset = queryset[:limit]
        results = OfficerCardSerializer(queryset, many=True).data

        return Response(results)
