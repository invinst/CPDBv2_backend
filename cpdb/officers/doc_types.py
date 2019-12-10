from elasticsearch_dsl import (
    DocType, Integer, Date, Float, Nested, InnerObjectWrapper, Text, Long, Boolean, Keyword
)

from .index_aliases import officers_index_alias

from search.analyzers import autocomplete, autocomplete_search


@officers_index_alias.doc_type
class OfficerCoaccusalsDocType(DocType):
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
    badge_keyword = Keyword()
    historic_badges_keyword = Keyword()
    tags = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    historic_badges = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    allegation_count = Long()
    has_visual_token = Boolean()
    complaint_percentile = Float()
    cr_incident_dates = Date()
    trr_datetimes = Date()

    historic_units = Nested(properties={
        'id': Integer(),
        'long_unit_name': Text(analyzer=autocomplete, search_analyzer=autocomplete_search),
        'description': Text(analyzer=autocomplete, search_analyzer=autocomplete_search),
    })

    @staticmethod
    def get_top_officers(percentile=99.0, size=40):
        query = OfficerInfoDocType.search().query(
            'bool',
            filter=[
                {'term': {'has_visual_token': True}},
                {'range': {'complaint_percentile': {'gte': percentile}}}
            ]
        )
        query = query.sort({'complaint_percentile': 'desc'})
        return query[0:size].execute()
