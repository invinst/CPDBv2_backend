from rest_framework import viewsets
from rest_framework.response import Response

from .doc_types import OfficerDocType
from .serializers import OfficerSerializer


class ReportBottomSheetOfficerSearchViewSet(viewsets.ViewSet):
    lookup_field = 'search_text'

    def retrieve(self, request, search_text):
        query = OfficerDocType().search().query('match', full_name=search_text)
        search_result = query[:5].execute()
        return Response(OfficerSerializer(search_result, many=True).data)
