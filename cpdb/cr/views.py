from rest_framework import viewsets, status
from rest_framework.response import Response

from .doc_types import CRDocType


class CRViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        query = CRDocType().search().query('term', crid=pk)
        search_result = query.execute()
        try:
            return Response(search_result[0].to_dict())
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)
