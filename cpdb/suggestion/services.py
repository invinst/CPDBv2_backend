from suggestion.doc_types import AutoComplete
from suggestion.autocomplete_types import AutoCompleteType


CONTENT_TYPES = [AutoCompleteType.OFFICER, AutoCompleteType.OFFICER_UNIT, AutoCompleteType.NEIGHBORHOOD]


class SuggestionService(object):
    def _build_completion(self, content_type, limit=None):
        completion = {
            'field': 'suggest',
            'context': {
                'content_type': content_type
            }
        }

        if limit:
            completion['size'] = limit

        return completion

    def suggest(self, term, suggest_content_type=None, limit=None):
        search = AutoComplete.search()
        content_types = suggest_content_type and [suggest_content_type] or CONTENT_TYPES

        for content_type in content_types:
            search = search.suggest(content_type, term, completion=self._build_completion(content_type, limit))

        suggestion = search.execute_suggest()
        return {
            key: val[0]['options']
            for key, val in suggestion.to_dict().items()
            if key in CONTENT_TYPES
        }
