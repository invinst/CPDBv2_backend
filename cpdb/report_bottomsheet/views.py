from rest_framework import viewsets
from rest_framework.response import Response

from .doc_types import OfficerDocType
from .serializers import OfficerDocTypeSerializer


class ReportBottomSheetOfficerSearchViewSet(viewsets.ViewSet):
    lookup_field = 'search_text'

    def retrieve(self, request, search_text):
        query = OfficerDocType().search().query('match', full_name=search_text)
        search_result = query[:3].execute()
        return Response(OfficerDocTypeSerializer(search_result, many=True).data)
