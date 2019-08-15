from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .doc_types import UnitDocType


class UnitsViewSet(viewsets.ViewSet):

    @action(detail=True, methods=['get'])
    def summary(self, request, pk):
        query = UnitDocType().search().query('term', unit_name=pk)
        search_result = query.execute()

        if len(search_result):
            return Response(search_result[0].to_dict())

        return Response(status=status.HTTP_404_NOT_FOUND)
