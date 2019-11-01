from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from data.models import Officer, AttachmentFile
from pinboard.models import Pinboard
from data.utils.attachment_file import filter_attachments
from social_graph.queries.social_graph_data_query import SocialGraphDataQuery
from social_graph.queries.geographic_data_query import GeographyCrsDataQuery, GeographyTrrsDataQuery
from social_graph.serializers import (
    OfficerDetailSerializer,
    SocialGraphCRDetailSerializer,
    CRSerializer,
    CRDetailSerializer,
    TRRSerializer,
    TRRDetailSerializer,
)

DEFAULT_LIMIT = 500


@method_decorator(never_cache, name='dispatch')
class SocialGraphBaseViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_path='network')
    def network(self, _):
        return Response(self._social_graph_data_query.graph_data())

    @action(detail=False, methods=['get'], url_path='allegations')
    def allegations(self, _):
        allegations = self._social_graph_data_query.allegations().select_related(
            'most_common_category'
        ).prefetch_related(
            Prefetch(
                'attachment_files',
                queryset=filter_attachments(AttachmentFile.objects),
                to_attr='prefetch_filtered_attachment_files'
            ),
            'officerallegation_set',
            'officerallegation_set__officer',
            'officerallegation_set__allegation_category',
            'victims',
        )

        return Response(SocialGraphCRDetailSerializer(allegations, many=True).data)

    @action(detail=False, methods=['get'], url_path='officers')
    def officers(self, _):
        return Response(
            OfficerDetailSerializer(
                self._social_graph_data_query.all_officers().select_related('last_unit'),
                many=True
            ).data
        )

    @action(detail=False, methods=['get'], url_path='geographic-crs')
    def geographic_crs(self, request):
        pinboard = self._pinboard
        crids = pinboard.crids if pinboard else []
        geographic_data_query = GeographyCrsDataQuery(crids, officers=self._data(False)['officers'])

        paginator = LimitOffsetPagination()
        paginator.default_limit = DEFAULT_LIMIT

        cr_data = geographic_data_query.data()

        if self._detail:
            cr_data = cr_data.prefetch_related(
                'officerallegation_set',
                'officerallegation_set__officer',
                'officerallegation_set__allegation_category',
                'victims',
            )

        paginated_cr_data = paginator.paginate_queryset(cr_data, request, view=self)
        serializer_klass = CRDetailSerializer if self._detail else CRSerializer
        serializer = serializer_klass(paginated_cr_data, many=True)

        return Response({
            'count': paginator.count,
            'limit': paginator.default_limit,
            'results': serializer.data
        })

    @action(detail=False, methods=['get'], url_path='geographic-trrs')
    def geographic_trrs(self, request):
        pinboard = self._pinboard
        trr_ids = pinboard.trr_ids if pinboard else []
        geographic_data_query = GeographyTrrsDataQuery(trr_ids, officers=self._data(False)['officers'])

        paginator = LimitOffsetPagination()
        paginator.default_limit = DEFAULT_LIMIT

        trr_data = geographic_data_query.data()

        if self._detail:
            trr_data = trr_data.select_related('officer')

        paginated_trr_data = paginator.paginate_queryset(trr_data, request, view=self)
        serializer_klass = TRRDetailSerializer if self._detail else TRRSerializer
        serializer = serializer_klass(paginated_trr_data, many=True)

        return Response({
            'count': paginator.count,
            'limit': paginator.default_limit,
            'results': serializer.data
        })

    @property
    def _social_graph_data_query(self):
        data = self._data()

        return SocialGraphDataQuery(
            pinboard_id=self._pinboard_id,
            officers=data['officers'],
            threshold=self._threshold,
            complaint_origin=self._complaint_origin,
            show_connected_officers=data['show_connected_officers']
        )

    def _data(self, include_connected_officers=True):
        pinboard = self._pinboard
        officer_ids = self._officer_ids
        unit_id = self._unit_id
        officers = []
        show_connected_officers = False
        if pinboard:
            show_connected_officers = self.PINBOARD_SHOW_CONNECTED_OFFICERS
            officers = pinboard.all_officers if include_connected_officers else pinboard.officers.all()
        elif officer_ids:
            officers = Officer.objects.filter(id__in=officer_ids.split(','))
        elif unit_id:
            officers = Officer.objects.filter(officerhistory__unit_id=unit_id).distinct()

        return {'officers': officers, 'show_connected_officers': show_connected_officers}

    @property
    def _pinboard(self):
        pinboard_id = self._pinboard_id
        if pinboard_id:
            queryset = Pinboard.objects.all()
            return get_object_or_404(queryset, id=pinboard_id)

    @property
    def _pinboard_id(self):
        return self.request.query_params.get('pinboard_id', None)

    @property
    def _unit_id(self):
        return self.request.query_params.get('unit_id', None)

    @property
    def _officer_ids(self):
        return self.request.query_params.get('officer_ids', None)

    @property
    def _threshold(self):
        return self.request.query_params.get('threshold', None)

    @property
    def _complaint_origin(self):
        return self.request.query_params.get('complaint_origin', None)

    @property
    def _detail(self):
        return self.request.query_params.get('detail', None)


class SocialGraphDesktopViewSet(SocialGraphBaseViewSet):
    PINBOARD_SHOW_CONNECTED_OFFICERS = True


class SocialGraphMobileViewSet(SocialGraphBaseViewSet):
    PINBOARD_SHOW_CONNECTED_OFFICERS = False
