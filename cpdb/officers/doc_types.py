from elasticsearch_dsl import DocType, Integer, Date, Keyword

from .indices import officers_index


@officers_index.doc_type
class OfficerSummaryDocType(DocType):
    id = Integer()


@officers_index.doc_type
class OfficerTimelineEventDocType(DocType):
    date_sort = Date(format='yyyy-MM-dd', include_in_all=False)
    year_sort = Integer()
    year_priority = Integer()
    kind = Keyword()
    officer_id = Integer()


@officers_index.doc_type
class OfficerTimelineMinimapDocType(DocType):
    officer_id = Integer()
