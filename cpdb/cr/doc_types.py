from elasticsearch_dsl import DocType, Keyword, GeoPoint, Nested, Integer, Float

from .index_aliases import cr_index_alias


@cr_index_alias.doc_type
class CRDocType(DocType):
    crid = Keyword()
    point = GeoPoint()
    category_names = Keyword()
    coaccused = Nested(
        properties={
            'percentile_allegation': Float(),
            'percentile_allegation_civilian': Float(),
            'percentile_allegation_internal': Float(),
            'percentile_trr': Float(),
            'id': Integer()
        })
    involvements = Nested(
        properties={
            'percentile_allegation': Float(),
            'percentile_allegation_civilian': Float(),
            'percentile_allegation_internal': Float(),
            'percentile_trr': Float(),
            'id': Integer()
        })

    class Meta:
        doc_type = 'cr_doc_type'
