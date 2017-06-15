from elasticsearch_dsl import DocType, Keyword
from .indices import units_index


@units_index.doc_type
class UnitDocType(DocType):
    unit_name = Keyword()
