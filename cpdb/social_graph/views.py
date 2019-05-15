from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from data.models import Officer, AttachmentFile
from data.utils.attachment_file import filter_attachments
from social_graph.queries.social_graph_data_query import SocialGraphDataQuery
from social_graph.queries.geographic_data_query import GeographyDataQuery
from social_graph.serializers import OfficerDetailSerializer, AllegationSerializer


class SocialGraphViewSet(viewsets.ViewSet):
    @list_route(methods=['get'], url_path='network')
    def network(self, _):
        social_graph_data_query = SocialGraphDataQuery(
            officers=self._officers,
            threshold=self._threshold,
            show_civil_only=self._show_civil_only,
        )

        return Response(social_graph_data_query.graph_data())

    @list_route(methods=['get'], url_path='allegations')
    def allegations(self, _):
        social_graph_data_query = SocialGraphDataQuery(
            officers=self._officers,
            threshold=self._threshold,
            show_civil_only=self._show_civil_only,
        )

        allegations = social_graph_data_query.allegations().select_related(
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
        social_graph_data_query = SocialGraphDataQuery(
            officers=self._officers,
            threshold=self._threshold,
            show_civil_only=self._show_civil_only,
        )

        return Response(
            OfficerDetailSerializer(
                social_graph_data_query.all_officers().select_related('last_unit'),
                many=True
            ).data
        )

    @list_route(methods=['get'], url_path='geographic')
    def geographic(self, _):
        geographic_data_query = GeographyDataQuery(officers=self._officers)
        return Response(geographic_data_query.execute())

    @property
    def _officers(self):
        officer_ids = self._officer_ids
        unit_id = self._unit_id
        officers = []
        if officer_ids:
            officers = Officer.objects.filter(id__in=officer_ids.split(','))
        elif unit_id:
            officers = Officer.objects.filter(officerhistory__unit_id=unit_id).distinct()

        return officers

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
        return self.request.query_params.get('show_civil_only', None)
