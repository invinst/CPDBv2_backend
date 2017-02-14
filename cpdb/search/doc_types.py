from elasticsearch_dsl import DocType, Text, InnerObjectWrapper, Nested

from .indices import autocompletes

from search.analyzers import autocomplete, autocomplete_search


@autocompletes.doc_type
class FAQDocType(DocType):
    question = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    answer = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)

    class Meta:
        doc_type = 'faq'


@autocompletes.doc_type
class ReportDocType(DocType):
    publication = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    author = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    title = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    excerpt = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)

    class Meta:
        doc_type = 'report'


@autocompletes.doc_type
class OfficerDocType(DocType):
    full_name = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    badge = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)

    class Meta:
        doc_type = 'officer'


@autocompletes.doc_type
class UnitDocType(DocType):
    name = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    description = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)

    class Meta:
        doc_type = 'unit'


@autocompletes.doc_type
class NeighborhoodsDocType(DocType):
    name = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)

    class Meta:
        doc_type = 'neighborhood'


@autocompletes.doc_type
class CommunityDocType(DocType):
    name = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)

    class Meta:
        doc_type = 'community'


@autocompletes.doc_type
class CoAccusedOfficerDocType(DocType):
    full_name = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    badge = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    co_accused_officer = Nested(doc_class=InnerObjectWrapper, properties={
        'full_name': Text(),
        'badge': Text()
        })

    class Meta:
        doc_type = 'coaccusedofficer'
