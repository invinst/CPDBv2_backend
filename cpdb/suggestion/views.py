from rest_framework import viewsets
from rest_framework.response import Response

from suggestion.services import SuggestionService


class SuggestionViewSet(viewsets.ViewSet):
    lookup_field = 'text'

    def retrieve(self, request, text):
        suggestions = SuggestionService().suggest(
            text, suggest_content_type=self._content_type, limit=self._limit)
        return Response(suggestions)

    @property
    def _limit(self):
        return self.request.query_params.get('limit', None)

    @property
    def _content_type(self):
        return self.request.query_params.get('contentType', None)
