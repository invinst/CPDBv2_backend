from rest_framework import viewsets, status
from rest_framework.response import Response

from trr.serializers.trr_response_serializers import TRRDesktopSerializer
from .doc_types import TRRDocType


class TRRViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        query = TRRDocType().search().query('term', id=pk)
        search_result = query.execute()
        try:
            return Response(TRRDesktopSerializer(search_result[0].to_dict()).data)
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)
