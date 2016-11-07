from suggestion.doc_types import AutoComplete
from suggestion.autocomplete_types import AutoCompleteType


LIMIT_BY_TYPE = 10
CONTEXT_TYPES = [AutoCompleteType.OFFICER, AutoCompleteType.OFFICER_UNIT, AutoCompleteType.NEIGHBORHOODS]


class SuggestionService(object):
    def suggest(self, term, context_types=None):
        search = AutoComplete.search()
        context_types = context_types or CONTEXT_TYPES

        for context in context_types:
            search = search.suggest(context, term, completion={
                'field': 'suggest',
                'size': LIMIT_BY_TYPE,
                'context': {
                    'content_type': context
                }
            })

        suggestion = search.execute_suggest()
        return {
            key: val[0]['options']
            for key, val in suggestion.to_dict().items()
            if key in CONTEXT_TYPES
        }
