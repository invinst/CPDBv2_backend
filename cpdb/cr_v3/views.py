from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import list_route
from django.shortcuts import get_object_or_404
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F

from cr_v3.serializers.cr_response_serializers import CRSerializer, CRSummarySerializer
from data.models import Allegation


class CRV3ViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        queryset = Allegation.objects.select_related('beat', 'most_common_category')
        allegation = get_object_or_404(queryset, crid=pk)
        serializer = CRSerializer(allegation)
        return Response(serializer.data)

    @list_route(methods=['GET'], url_path='complaint-summaries')
    def complaint_summaries(self, request):
        query = Allegation.objects.filter(
            summary__isnull=False
        ).exclude(
            summary__exact=''
        ).annotate(
            categories=ArrayAgg('officerallegation__allegation_category__category')
        ).only(
            'crid', 'summary', 'incident_date'
        ).order_by(F('incident_date').desc(nulls_last=True), '-crid')[:40]
        return Response(CRSummarySerializer(query, many=True).data, status=status.HTTP_200_OK)
