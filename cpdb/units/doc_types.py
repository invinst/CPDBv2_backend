from elasticsearch_dsl import DocType, Keyword
from .index_aliases import units_index_alias


@units_index_alias.doc_type
class UnitDocType(DocType):
    unit_name = Keyword()
