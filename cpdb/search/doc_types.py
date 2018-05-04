from elasticsearch_dsl import DocType, Text, Long, Keyword, Float

from .indices import autocompletes_alias

from search.analyzers import autocomplete, autocomplete_search


@autocompletes_alias.doc_type
class FAQDocType(DocType):
    question = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    answer = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    tags = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)

    class Meta:
        doc_type = 'faq'


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
class OfficerDocType(DocType):
    full_name = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    badge = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    tags = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    allegation_count = Long()

    class Meta:
        doc_type = 'officer'


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
    allegation_percentile = Float()

    class Meta:
        doc_type = 'area'


@autocompletes_alias.doc_type
class UnitOfficerDocType(DocType):
    allegation_count = Long()
    unit_name = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    unit_description = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    tags = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)

    class Meta:
        doc_type = 'unitofficer'


@autocompletes_alias.doc_type
class CrDocType(DocType):
    crid = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)

    class Meta:
        doc_type = 'cr'
