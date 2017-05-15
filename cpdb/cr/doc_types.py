from elasticsearch_dsl import DocType, Keyword

from .indices import cr_index


@cr_index.doc_type
class CRDocType(DocType):
    crid = Keyword()
