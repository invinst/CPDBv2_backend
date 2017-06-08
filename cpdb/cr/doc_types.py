from elasticsearch_dsl import DocType, Keyword

from .index_aliases import cr_index_alias


@cr_index_alias.doc_type
class CRDocType(DocType):
    crid = Keyword()
