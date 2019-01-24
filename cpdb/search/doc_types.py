from elasticsearch_dsl import DocType, Text, Keyword, Float, Integer, String

from .indices import autocompletes_alias

from search.analyzers import autocomplete, autocomplete_search


@autocompletes_alias.doc_type
class ReportDocType(DocType):
    publication = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    author = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    title = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    excerpt = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    tags = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)

    class Meta:
        doc_type = 'report'


@autocompletes_alias.doc_type
class UnitDocType(DocType):
    long_name = Text(analyzer=autocomplete, search_analyzer=autocomplete_search, fields={'keyword': Keyword()})
    description = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    tags = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)

    class Meta:
        doc_type = 'unit'


@autocompletes_alias.doc_type
class AreaDocType(DocType):
    name = Text(analyzer=autocomplete, search_analyzer=autocomplete_search, fields={'keyword': Keyword()})
    tags = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    area_type = Keyword()
    allegation_count = Integer()
    allegation_percentile = Float()

    class Meta:
        doc_type = 'area'


@autocompletes_alias.doc_type
class RankDocType(DocType):
    rank = Text(analyzer=autocomplete, search_analyzer=autocomplete_search, fields={'keyword': Keyword()})
    tags = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    active_officers_count = Integer()

    class Meta:
        doc_type = 'rank'


@autocompletes_alias.doc_type
class CrDocType(DocType):
    crid = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    incident_date = Keyword()
    summary = Text(analyzer='standard', store=True, term_vector="with_positions_offsets")
    investigator_names = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)

    class Meta:
        doc_type = 'cr'


@autocompletes_alias.doc_type
class TRRDocType(DocType):
    id = Integer()
    trr_datetime = Keyword()

    class Meta:
        doc_type = 'trr'


@autocompletes_alias.doc_type
class ZipCodeDocType(DocType):
    id = Integer()
    zip_code = Text(analyzer=autocomplete, search_analyzer=autocomplete_search, fields={'keyword': Keyword()})
    tags = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)

    class Meta:
        doc_type = 'zip_code'


@autocompletes_alias.doc_type
class SearchTermItemDocType(DocType):
    slug = String(index='not_analyzed')
    name = Text(analyzer=autocomplete, search_analyzer=autocomplete_search, fields={'keyword': Keyword()})
    category_name = Text(
        fielddata=True,
        analyzer=autocomplete,
        search_analyzer=autocomplete_search,
        fields={'keyword': Keyword()}
    )

    class Meta:
        doc_type = 'search_term_item'
