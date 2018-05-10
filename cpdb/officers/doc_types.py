from elasticsearch_dsl import DocType, Integer, Date, Keyword, Float, Nested, InnerObjectWrapper, Q, Text, Long

from .index_aliases import officers_index_alias

from search.analyzers import autocomplete, autocomplete_search


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

    @staticmethod
    def _get_latest_year():
        query = OfficerInfoDocType.search()
        query.aggs.bucket('percentiles', 'nested', path='percentiles') \
            .metric('max_year', 'max', field='percentiles.year')
        query = query.execute()
        max_year = query.aggregations.percentiles.max_year.value
        return max_year if max_year else 0

    @staticmethod
    def get_top_officers(percentile=99.0, size=40):
        lastest_year = OfficerInfoDocType._get_latest_year()
        query = OfficerInfoDocType.search().query('nested', path='percentiles', query=Q(
            'bool',
            filter=[
                {'term': {'percentiles.year': lastest_year}},
                {'range': {'percentiles.percentile_allegation': {'gte': percentile}}}
            ]
        ))
        query = query.sort({
            'percentiles.percentile_allegation': {
                "order": "desc",
                "mode": "max",
                "nested_path": "percentiles",
                "nested_filter": {
                    "term": {"percentiles.year": lastest_year}
                }
            }}
        )

        return query[0:size].execute()
