from elasticsearch_dsl import DocType, Text, Long

from es_index.analyzers import autocomplete_analyzer, autocomplete_search_analyzer
from .index_aliases import twitterbot_index_alias


@twitterbot_index_alias.doc_type
class OfficerDocType(DocType):
    full_name = Text(analyzer=autocomplete_analyzer, search_analyzer=autocomplete_search_analyzer)
    allegation_count = Long()

    class Meta:
        doc_type = 'officer'
