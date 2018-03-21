from elasticsearch_dsl import DocType, Keyword, GeoPoint, Nested, Integer

from .index_aliases import cr_index_alias


@cr_index_alias.doc_type
class CRDocType(DocType):
    crid = Keyword()
    point = GeoPoint()
    category_names = Keyword()
    coaccused = Nested(
        properties={
            'id': Integer()
        })
