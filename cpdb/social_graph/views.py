from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from data.models import Officer, AttachmentFile
from pinboard.models import Pinboard
from data.utils.attachment_file import filter_attachments
from social_graph.queries.social_graph_data_query import SocialGraphDataQuery
from social_graph.queries.geographic_data_query import GeographyDataQuery
from social_graph.serializers.officer_detail_serializer import OfficerDetailSerializer
from social_graph.serializers.allegation_serializer import AllegationSerializer


@method_decorator(never_cache, name='dispatch')
class SocialGraphBaseViewSet(viewsets.ViewSet):
    @list_route(methods=['get'], url_path='network')
    def network(self, _):
        return Response(self._social_graph_data_query.graph_data())

    @list_route(methods=['get'], url_path='allegations')
    def allegations(self, _):
        allegations = self._social_graph_data_query.allegations().select_related(
            'most_common_category'
        ).prefetch_related(
            Prefetch(
                'attachment_files',
                queryset=filter_attachments(AttachmentFile.objects),
                to_attr='prefetch_filtered_attachment_files'
            )
        )

        return Response(AllegationSerializer(allegations, many=True).data)

    @list_route(methods=['get'], url_path='officers')
    def officers(self, _):
        return Response(
            OfficerDetailSerializer(
                self._social_graph_data_query.all_officers().select_related('last_unit'),
                many=True
            ).data
        )

    @list_route(methods=['get'], url_path='geographic')
    def geographic(self, _):
        geographic_data_query = GeographyDataQuery(officers=self._data['officers'])
        return Response(geographic_data_query.execute())

    @property
    def _social_graph_data_query(self):
        data = self._data

        return SocialGraphDataQuery(
            officers=data['officers'],
            threshold=self._threshold,
            show_civil_only=self._show_civil_only,
            show_connected_officers=data['show_connected_officers']
        )

    @property
    def _data(self):
        pinboard_id = self._pinboard_id
        officer_ids = self._officer_ids
        unit_id = self._unit_id
        officers = []
        show_connected_officers = False
        if pinboard_id:
            queryset = Pinboard.objects.all()
            pinboard = get_object_or_404(queryset, id=pinboard_id)
            show_connected_officers = self.PINBOARD_SHOW_CONNECTED_OFFICERS
            officers = pinboard.all_officers
        elif officer_ids:
            officers = Officer.objects.filter(id__in=officer_ids.split(','))
        elif unit_id:
            officers = Officer.objects.filter(officerhistory__unit_id=unit_id).distinct()

        return {'officers': officers, 'show_connected_officers': show_connected_officers}

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
    def _show_civil_only(self):
        show_civil_only = self.request.query_params.get('show_civil_only', None)
        return show_civil_only and show_civil_only.capitalize() == 'True'


class SocialGraphDesktopViewSet(SocialGraphBaseViewSet):
    PINBOARD_SHOW_CONNECTED_OFFICERS = True

    @list_route(methods=['get'], url_path='detail-geographic')
    def detail_geographic(self, _):
        detail_geographic_data_query = GeographyDataQuery(officers=self._data['officers'], detail=True)
        return Response(detail_geographic_data_query.execute())


class SocialGraphMobileViewSet(SocialGraphBaseViewSet):
    PINBOARD_SHOW_CONNECTED_OFFICERS = False
