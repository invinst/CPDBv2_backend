from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from .doc_types import OfficerSummaryDocType


class OfficersViewSet(viewsets.ViewSet):
    @detail_route(methods=['get'])
    def summary(self, request, pk):
        query = OfficerSummaryDocType().search().query('term', id=pk)
        search_result = query.execute()
        try:
            return Response(search_result[0].to_dict())
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)
