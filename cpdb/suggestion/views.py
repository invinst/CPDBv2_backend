from rest_framework import viewsets
from rest_framework.response import Response

from suggestion.services import SuggestionService


class SuggestionViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response(SuggestionService().suggest(request.query_params.get('text')))
