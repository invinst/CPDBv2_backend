from elasticsearch_dsl.query import Q
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route

from activity_grid.serializers import OfficerCardSerializer
from data.models import Officer
from es_index.pagination import ESQueryPagination
from officers.serializers import (NewTimelineSerializer, TimelineSerializer)
from .doc_types import (
    OfficerTimelineEventDocType,
    OfficerInfoDocType,
    OfficerNewTimelineEventDocType,
    OfficerSocialGraphDocType,
    OfficerCoaccusalsDocType
)

_ALLOWED_FILTERS = [
    'category',
    'race',
    'gender',
    'age',
]


class OfficersViewSet(viewsets.ViewSet):
    @detail_route(methods=['get'])
    def summary(self, request, pk):
        query = OfficerInfoDocType().search().query('term', id=pk)
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

    def _query_new_timeline_items(self, pk):
        sort_order = ['-date_sort', '-priority_sort']
        return OfficerNewTimelineEventDocType().search().sort(*sort_order).query('term', officer_id=pk)

    @detail_route(methods=['get'], url_path='new-timeline-items')
    def new_timeline_items(self, _, pk):
        if Officer.objects.filter(pk=pk).exists():
            query = self._query_new_timeline_items(pk)
            result = query[:10000].execute()
            return Response(NewTimelineSerializer(result, many=True).data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @detail_route(methods=['get'], url_path='social-graph')
    def social_graph(self, request, pk):
        query = OfficerSocialGraphDocType().search().query('term', officer_id=pk)
        search_result = query.execute()
        try:
            return Response(search_result[0].to_dict()['graph'])
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @list_route(methods=['get'], url_path='top-by-allegation')
    def top_officers_by_allegation(self, request):
        limit = request.GET.get('limit', 40)
        top_officers = OfficerInfoDocType.get_top_officers(percentile=99.0, size=limit)

        return Response(OfficerCardSerializer(top_officers, many=True).data)

    @detail_route(methods=['get'])
    def coaccusals(self, _, pk):
        query = OfficerCoaccusalsDocType().search().query('term', id=pk)
        result = query.execute()
        try:
            return Response(result[0].to_dict()['coaccusals'])
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)
