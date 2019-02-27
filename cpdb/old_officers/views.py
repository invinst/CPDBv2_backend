from rest_framework import viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from data.models import Officer
from old_officers.serializers.respone_serialiers import (
    DesktopTimelineSerializer,
    OfficerMobileSerializer,
    MobileTimelineSerializer,
)
from officers.doc_types import (
    OfficerInfoDocType,
    OfficerNewTimelineEventDocType,
    OfficerCoaccusalsDocType,
)

_ALLOWED_FILTERS = [
    'category',
    'race',
    'gender',
    'age',
]


class OldOfficersViewSet(viewsets.ViewSet):
    @detail_route(methods=['get'])
    def summary(self, request, pk):
        query = OfficerInfoDocType().search().source(
            excludes=['cr_incident_dates', 'trr_datetimes']
        ).query('term', id=pk)
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
            return Response(DesktopTimelineSerializer(result, many=True).data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @detail_route(methods=['get'])
    def coaccusals(self, _, pk):
        query = OfficerCoaccusalsDocType().search().query('term', id=pk)
        result = query.execute()
        try:
            return Response(result[0].to_dict()['coaccusals'])
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response([])


class OldOfficersMobileViewSet(viewsets.ViewSet):
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
            return Response(MobileTimelineSerializer(result, many=True).data)
        return Response(status=status.HTTP_404_NOT_FOUND)
