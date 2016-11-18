from rest_framework import viewsets
from rest_framework.response import Response

from suggestion.doc_types import AutoComplete
from suggestion.autocomplete_types import AutoCompleteType


LIMIT_BY_TYPE = 8
CONTEXT_TYPES = [AutoCompleteType.OFFICER, AutoCompleteType.OFFICER_UNIT, AutoCompleteType.NEIGHBORHOODS]


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
        results = {
            key: val[0]['options']
            for key, val in suggestion.to_dict().items()
            if key in CONTEXT_TYPES
        }
        return Response(results)
