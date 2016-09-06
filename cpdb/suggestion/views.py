from rest_framework import viewsets
from rest_framework.response import Response

from suggestion.doc_types import AutoComplete


class SuggestionViewSet(viewsets.ViewSet):
    def list(self, request):
        suggest = AutoComplete.search()\
            .suggest('auto_complete', request.query_params.get('text'), completion={'field': 'suggest'})
        suggestions = suggest.execute_suggest()
        return Response(suggestions.auto_complete[0].to_dict())
