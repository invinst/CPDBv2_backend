from elasticsearch_dsl import DocType, Completion, analyzer

from suggestion.indexes import autocompletes


@autocompletes.doc_type
class AutoComplete(DocType):
    suggest = Completion(payloads=True, analyzer=analyzer('english'), context={
        'content_type': {
            'type': 'category'
        }
    })
