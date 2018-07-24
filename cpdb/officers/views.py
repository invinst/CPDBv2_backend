from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from activity_grid.serializers import OfficerCardSerializer
from data.models import Officer
from officers.serializers.respone_serialiers import NewTimelineSerializer, OfficerMobileSerializer
from .doc_types import (
    OfficerInfoDocType,
    OfficerNewTimelineEventDocType,
    OfficerSocialGraphDocType,
    OfficerCoaccusalsDocType,
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
        limit = int(request.GET.get('limit', 40))
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


class OfficersMobileViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        query = OfficerInfoDocType().search().query('term', id=pk)
        search_result = query.execute()
        try:
            return Response(OfficerMobileSerializer(search_result[0].to_dict()).data)
        except IndexError:
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
