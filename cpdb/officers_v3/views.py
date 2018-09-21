from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from data.models import Officer
from officers.doc_types import OfficerCoaccusalsDocType
from officers_v3.seriallizers.respone_serialiers import OfficerInfoSerializer, OfficerCardSerializer
from officers_v3.queries import OfficerTimelineQuery


class OfficersV3ViewSet(viewsets.ViewSet):
    @detail_route(methods=['get'])
    def summary(self, request, pk):
        queryset = Officer.objects.all()
        officer = get_object_or_404(queryset, id=pk)
        return Response(OfficerInfoSerializer(officer).data)

    @detail_route(methods=['get'], url_path='new-timeline-items')
    def new_timeline_items(self, _, pk):
        queryset = Officer.objects.all()
        officer = get_object_or_404(queryset, id=pk)
        return Response(OfficerTimelineQuery(officer).execute())

    @list_route(methods=['get'], url_path='top-by-allegation')
    def top_officers_by_allegation(self, request):
        limit = int(request.GET.get('limit', 40))

        top_officers = Officer.objects.filter(
            complaint_percentile__gte=99.0,
            civilian_allegation_percentile__isnull=False,
            internal_allegation_percentile__isnull=False,
            trr_percentile__isnull=False,
        ).order_by('-complaint_percentile')[:limit]
        return Response(OfficerCardSerializer(top_officers, many=True).data)

    @detail_route(methods=['get'])
    def coaccusals(self, _, pk):
        query = OfficerCoaccusalsDocType().search().query('term', id=pk)
        result = query.execute()
        try:
            return Response(result[0].to_dict()['coaccusals'])
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)
