from django.db.models import Case, When
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from data.models import Officer, OfficerAlias
from analytics.models import AttachmentTracking
from officers.queries import OfficerTimelineQuery, OfficerTimelineMobileQuery
from officers.serializers.response_mobile_serializers import (
    OfficerInfoMobileSerializer,
    CoaccusalCardMobileSerializer, OfficerCardMobileSerializer,
)
from officers.serializers.response_serializers import (
    OfficerInfoSerializer, OfficerCardSerializer, OfficerCoaccusalSerializer,
)

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
    @action(detail=True, methods=['get'])
    def summary(self, _, pk):
        officer_id = self.get_officer_id(pk)
        queryset = Officer.objects.all()
        officer = get_object_or_404(queryset, id=officer_id)
        return Response(OfficerInfoSerializer(officer).data)

    @action(detail=True, methods=['get'], url_path='new-timeline-items')
    def new_timeline_items(self, _, pk):
        officer_id = self.get_officer_id(pk)
        queryset = Officer.objects.all()
        officer = get_object_or_404(queryset, id=officer_id)
        return Response(OfficerTimelineQuery(officer).execute())

    @action(detail=False, methods=['get'], url_path='top-by-allegation', url_name='top-by-allegation')
    def top_officers_by_allegation(self, request):
        limit = int(request.GET.get('limit', 40))

        top_officers = Officer.objects.filter(
            complaint_percentile__gte=99.0,
            civilian_allegation_percentile__isnull=False,
            internal_allegation_percentile__isnull=False,
            trr_percentile__isnull=False,
        ).order_by('-complaint_percentile')[:limit]
        return Response(OfficerCardSerializer(top_officers, many=True).data)

    @action(detail=True, methods=['get'])
    def coaccusals(self, _, pk):
        officer_id = self.get_officer_id(pk)
        queryset = Officer.objects.all()
        officer = get_object_or_404(queryset, id=officer_id)
        return Response(OfficerCoaccusalSerializer(officer.coaccusals, many=True).data)

    def list(self, request):
        ids_str = request.GET.get('ids', '')

        officer_ids = []
        invalid_officer_ids = []
        for officer_id in ids_str.split(','):
            try:
                officer_ids.append(int(officer_id))
            except ValueError:
                invalid_officer_ids.append(officer_id)

        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(officer_ids)])
        officers = Officer.objects.filter(id__in=officer_ids).order_by(preserved)

        invalid_officer_ids = invalid_officer_ids + list(set(officer_ids) - {o.id for o in officers})

        if invalid_officer_ids:
            return Response(
                f"Invalid officer ids: {', '.join(map(str, invalid_officer_ids))}",
                status.HTTP_400_BAD_REQUEST
            )

        return Response(OfficerCardSerializer(officers, many=True).data)

    @action(detail=True, methods=['get'], url_path='request-download')
    def request_download(self, request, pk):
        officer_id = self.get_officer_id(pk)
        queryset = Officer.objects.all()
        officer = get_object_or_404(queryset, id=officer_id)

        with_docs = request.GET.get('with-docs', '') == 'true'

        if with_docs:
            AttachmentTracking.objects.create_attachment_download_events(
                list(officer.allegation_attachments) + list(officer.investigator_attachments)
            )

        if officer.check_zip_file_exist(with_docs=with_docs):
            url = officer.generate_presigned_zip_url(with_docs=with_docs)
        else:
            url = ''
        return Response(data=url)

    @action(detail=True, methods=['get'], url_path='create-zip-file')
    def create_zip_file(self, _, pk):
        officer_id = self.get_officer_id(pk)
        queryset = Officer.objects.all()
        officer = get_object_or_404(queryset, id=officer_id)
        officer.invoke_create_zip(with_docs=True)
        officer.invoke_create_zip(with_docs=False)
        return Response()


class OfficersMobileViewSet(OfficerBaseViewSet):
    def retrieve(self, _, pk):
        officer_id = self.get_officer_id(pk)
        queryset = Officer.objects.all()
        officer = get_object_or_404(queryset, id=officer_id)
        return Response(OfficerInfoMobileSerializer(officer).data)

    @action(detail=True, methods=['get'], url_path='new-timeline-items')
    def new_timeline_items(self, _, pk):
        officer_id = self.get_officer_id(pk)
        queryset = Officer.objects.all()
        officer = get_object_or_404(queryset, id=officer_id)
        return Response(OfficerTimelineMobileQuery(officer).execute())

    @action(detail=True, methods=['get'])
    def coaccusals(self, _, pk):
        officer_id = self.get_officer_id(pk)
        queryset = Officer.objects.all()
        officer = get_object_or_404(queryset, id=officer_id)
        return Response(CoaccusalCardMobileSerializer(officer.coaccusals, many=True).data)

    def list(self, request):
        ids_str = request.GET.get('ids', '')

        officer_ids = []
        invalid_officer_ids = []
        for officer_id in ids_str.split(','):
            try:
                officer_ids.append(int(officer_id))
            except ValueError:
                invalid_officer_ids.append(officer_id)

        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(officer_ids)])
        officers = Officer.objects.filter(id__in=officer_ids).order_by(preserved)

        invalid_officer_ids = invalid_officer_ids + list(set(officer_ids) - {o.id for o in officers})

        if invalid_officer_ids:
            return Response(
                f"Invalid officer ids: {', '.join(map(str, invalid_officer_ids))}",
                status.HTTP_400_BAD_REQUEST
            )
        return Response(OfficerCardMobileSerializer(officers, many=True).data)
