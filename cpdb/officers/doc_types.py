from elasticsearch_dsl import DocType, Integer, Date, Keyword, Float

from .index_aliases import officers_index_alias


@officers_index_alias.doc_type
class OfficerSummaryDocType(DocType):
    id = Integer()


@officers_index_alias.doc_type
class OfficerMetricsDocType(DocType):
    id = Integer()


@officers_index_alias.doc_type
class OfficerTimelineEventDocType(DocType):
    date_sort = Date(format='yyyy-MM-dd', include_in_all=False)
    year_sort = Integer()
    priority_sort = Integer()
    kind = Keyword()
    officer_id = Integer()


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


@officers_index_alias.doc_type
class OfficerPercentileDocType(DocType):
    officer_id = Integer()
    year = Integer()
    percentile_trr = Float()
    percentile_allegation = Float()
    percentile_allegation_internal = Float()
    percentile_allegation_civilian = Float()
