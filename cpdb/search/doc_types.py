from elasticsearch_dsl import DocType, Text, Keyword, Float, Integer

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
    name = Text(analyzer=autocomplete, search_analyzer=autocomplete_search, fields={'keyword': Keyword()})
    description = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)

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
class CrDocType(DocType):
    crid = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)

    class Meta:
        doc_type = 'cr'


@autocompletes_alias.doc_type
class TRRDocType(DocType):
    id = Integer()

    class Meta:
        doc_type = 'trr'
