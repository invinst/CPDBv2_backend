from elasticsearch_dsl.query import Q
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route

from activity_grid.serializers import OfficerCardSerializer
from data.models import Officer
from es_index.pagination import ESQueryPagination
from officers.doc_types import OfficerSocialGraphDocType, OfficerPercentileDocType
from officers.serializers import OfficerYearlyPercentileSerializer
from officers.workers import OfficerPercentileWorker, OfficerMetricsWorker
from .doc_types import OfficerSummaryDocType, OfficerTimelineEventDocType, OfficerMetricsDocType
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

    @detail_route(methods=['get'])
    def metrics(self, request, pk):
        query = OfficerMetricsDocType().search().query('term', id=pk)
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
        limit = request.GET.get('limit', 40)
        top_officers_percentile = OfficerPercentileWorker().get_top_officers(size=limit)
        ids = [p.officer_id for p in top_officers_percentile]
        queryset = Officer.objects.filter(id__in=ids)

        officers = {h.id: h for h in queryset}
        es_results = OfficerMetricsWorker().search(ids, size=limit)
        metric_data = {h.id: h.to_dict() for h in es_results.hits}
        results = []
        for percentile in top_officers_percentile:
            obj = officers[percentile.officer_id]
            obj.percentile = percentile
            if percentile.officer_id in metric_data:
                officer_metric = metric_data[percentile.officer_id]
                obj.sustained_count_metric = officer_metric['sustained_count']
                obj.complaint_count_metric = officer_metric['allegation_count']
            results.append(obj)

        return Response(OfficerCardSerializer(results, many=True).data)
