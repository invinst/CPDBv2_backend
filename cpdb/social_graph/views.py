from rest_framework import viewsets
from rest_framework.response import Response

from data.models import Officer
from social_graph.queries import SocialGraphDataQuery


class SocialGraphViewSet(viewsets.ViewSet):
    def list(self, _):
        officer_ids = self._officer_ids
        unit_id = self._unit_id
        officers = []
        if officer_ids:
            officers = Officer.objects.filter(id__in=officer_ids.split(','))
        elif unit_id:
            officers = Officer.objects.filter(officerhistory__unit_id=unit_id).distinct()

        social_graph_data_query = SocialGraphDataQuery(officers, self._threshold, self._show_civil_only)

        return Response(social_graph_data_query.graph_data)

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
