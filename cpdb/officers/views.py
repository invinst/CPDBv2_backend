from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from data.models import Officer, OfficerAlias
from officers.serializers.response_serializers import (
    OfficerInfoSerializer, OfficerCardSerializer, OfficerCoaccusalSerializer
)
from officers.serializers.response_mobile_serializers import OfficerInfoMobileSerializer, OfficerCardMobileSerializer
from officers.queries import OfficerTimelineQuery, OfficerTimelineMobileQuery

_ALLOWED_FILTERS = [
    'category',
    'race',
    'gender',
    'age',
]


class OfficerBaseViewSet(viewsets.ViewSet):
    def get_officer_id(self, pk):
        """
        If an officer id does not exist, return the alias id if possible.
        Frontend should be able to detect that there is a change in officer
        id and redirect accordingly.
        """
        try:
            alias = OfficerAlias.objects.get(old_officer_id=pk)
            return alias.new_officer_id
        except OfficerAlias.DoesNotExist:
            return pk


class OfficersDesktopViewSet(OfficerBaseViewSet):
    @detail_route(methods=['get'])
    def summary(self, _, pk):
        officer_id = self.get_officer_id(pk)
        queryset = Officer.objects.all()
        officer = get_object_or_404(queryset, id=officer_id)
        return Response(OfficerInfoSerializer(officer).data)

    @detail_route(methods=['get'], url_path='new-timeline-items')
    def new_timeline_items(self, _, pk):
        officer_id = self.get_officer_id(pk)
        queryset = Officer.objects.all()
        officer = get_object_or_404(queryset, id=officer_id)
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
        officer_id = self.get_officer_id(pk)
        queryset = Officer.objects.all()
        officer = get_object_or_404(queryset, id=officer_id)
        return Response(OfficerCoaccusalSerializer(officer.coaccusals, many=True).data)


class OfficersMobileViewSet(OfficerBaseViewSet):
    def retrieve(self, _, pk):
        officer_id = self.get_officer_id(pk)
        queryset = Officer.objects.all()
        officer = get_object_or_404(queryset, id=officer_id)
        return Response(OfficerInfoMobileSerializer(officer).data)

    @detail_route(methods=['get'], url_path='new-timeline-items')
    def new_timeline_items(self, _, pk):
        officer_id = self.get_officer_id(pk)
        queryset = Officer.objects.all()
        officer = get_object_or_404(queryset, id=officer_id)
        return Response(OfficerTimelineMobileQuery(officer).execute())

    @detail_route(methods=['get'])
    def coaccusals(self, _, pk):
        officer_id = self.get_officer_id(pk)
        queryset = Officer.objects.all()
        officer = get_object_or_404(queryset, id=officer_id)
        return Response(OfficerCardMobileSerializer(officer.coaccusals, many=True).data)
