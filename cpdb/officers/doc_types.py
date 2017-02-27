from elasticsearch_dsl import DocType, Integer

from .indices import officers_index


@officers_index.doc_type
class OfficerSummaryDocType(DocType):
    id = Integer()
