from elasticsearch_dsl import DocType, Integer, Date, Keyword, Float, Nested, InnerObjectWrapper, Text, Long, Boolean

from .index_aliases import officers_index_alias

from search.analyzers import autocomplete, autocomplete_search


@officers_index_alias.doc_type
class OfficerNewTimelineEventDocType(DocType):
    date_sort = Date(format='yyyy-MM-dd', include_in_all=False)
    priority_sort = Integer()
    kind = Keyword()
    officer_id = Integer()


@officers_index_alias.doc_type
class OfficerCoaccusalsDocType(DocType):
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
    full_name = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    badge = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    tags = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    historic_badges = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    allegation_count = Long()
    has_visual_token = Boolean()
    current_allegation_percentile = Float()

    historic_units = Nested(properties={
        "id": Integer(),
        "unit_name": Text(analyzer=autocomplete, search_analyzer=autocomplete_search),
        "description": Text(analyzer=autocomplete, search_analyzer=autocomplete_search),
    })

    @staticmethod
    def get_top_officers(percentile=99.0, size=40):
        query = OfficerInfoDocType.search().query(
            'bool',
            filter=[
                {'term': {'has_visual_token': True}},
                {'range': {'current_allegation_percentile': {'gte': percentile}}}
            ]
        )
        query = query.sort({'current_allegation_percentile': 'desc'})
        return query[0:size].execute()
