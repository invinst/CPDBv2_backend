from rest_framework import viewsets
from rest_framework.response import Response

from suggestion.doc_types import AutoComplete


LIMIT_BY_TYPE = 5
CONTEXT_TYPES = ['officer_name', 'officer_badge_number', 'neighborhoods']


class SuggestionViewSet(viewsets.ViewSet):
    def list(self, request):
        search = AutoComplete.search()

        for context in CONTEXT_TYPES:
            search = search.suggest(context, request.query_params.get('text'), completion={
                'field': 'suggest',
                'size': LIMIT_BY_TYPE,
                'context': {
                    'content_type': context
                }
            })

        suggestion = search.execute_suggest()
        return Response(suggestion.to_dict())
