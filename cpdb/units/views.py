from rest_framework import viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from .doc_types import UnitDocType


class UnitsViewSet(viewsets.ViewSet):

    @detail_route(methods=['get'])
    def summary(self, request, pk):
        query = UnitDocType().search().query('term', unit_name=pk)
        search_result = query.execute()
        try:
            return Response(search_result[0].to_dict())
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
