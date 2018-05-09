from elasticsearch_dsl import DocType, Text

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
class UnitDocType(DocType):
    name = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    description = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)

    class Meta:
        doc_type = 'unit'


@autocompletes_alias.doc_type
class NeighborhoodsDocType(DocType):
    name = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    tags = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)

    class Meta:
        doc_type = 'neighborhood'


@autocompletes_alias.doc_type
class CommunityDocType(DocType):
    name = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    tags = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)

    class Meta:
        doc_type = 'community'


@autocompletes_alias.doc_type
class CrDocType(DocType):
    crid = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)

    class Meta:
        doc_type = 'cr'
