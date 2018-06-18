from elasticsearch_dsl import DocType, Keyword, Float, Nested, Integer

from .index_aliases import trr_index_alias


@trr_index_alias.doc_type
class TRRDocType(DocType):
    trr_id = Keyword()

    officer = Nested(
        properties={
            'id': Integer(),
            'percentile_allegation_civilian': Float(),
            'percentile_allegation_internal': Float(),
            'percentile_trr': Float(),
        })

    class Meta:
        doc_type = 'trr_doc_type'
