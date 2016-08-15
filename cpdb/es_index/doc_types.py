from elasticsearch_dsl import DocType, Completion, analyzer

from es_index.indexes import autocompletes


@autocompletes.doc_type
class AutoComplete(DocType):
    suggest = Completion(payloads=True, analyzer=analyzer('english'))
