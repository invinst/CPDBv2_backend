from elasticsearch_dsl import DocType, Integer, Date, Keyword, Float, Nested, InnerObjectWrapper

from .index_aliases import officers_index_alias


@officers_index_alias.doc_type
class OfficerNewTimelineEventDocType(DocType):
    date_sort = Date(format='yyyy-MM-dd', include_in_all=False)
    priority_sort = Integer()
    kind = Keyword()
    officer_id = Integer()


@officers_index_alias.doc_type
class OfficerTimelineMinimapDocType(DocType):
    officer_id = Integer()


@officers_index_alias.doc_type
class OfficerSocialGraphDocType(DocType):
    officer_id = Integer()


class OfficerYearlyPercentile(InnerObjectWrapper):
    @staticmethod
    def mapping():
        return {
            'year': Integer(),
            'percentile_trr': Float(),
            'percentile_allegation': Float(),
            'percentile_allegation_internal': Float(),
            'percentile_allegation_civilian': Float(),
        }


@officers_index_alias.doc_type
class OfficerInfoDocType(DocType):
    id = Integer()
    percentiles = Nested(
        doc_class=OfficerYearlyPercentile,
        properties=OfficerYearlyPercentile.mapping())
