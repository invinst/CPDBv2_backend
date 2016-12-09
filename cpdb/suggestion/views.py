from rest_framework import viewsets
from rest_framework.response import Response

from suggestion.services import SuggestionService


class SuggestionViewSet(viewsets.ViewSet):
    lookup_field = 'text'
    SUGGESTION_PER_TYPE = 10

    def retrieve(self, request, text):
        suggestions = SuggestionService().suggest(
            text, suggest_content_type=self._content_type, limit=self.SUGGESTION_PER_TYPE)
        return Response(suggestions)

    @property
    def _content_type(self):
        return self.request.query_params.get('contentType', None)
