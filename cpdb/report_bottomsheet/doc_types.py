from elasticsearch_dsl import DocType, Text, Integer

from es_index.analyzers import autocomplete_analyzer, autocomplete_search_analyzer
from .indices import report_bottomsheet_index


@report_bottomsheet_index.doc_type
class OfficerDocType(DocType):
    full_name = Text(analyzer=autocomplete_analyzer, search_analyzer=autocomplete_search_analyzer)
    allegation_count = Integer(index=False, store=True)
    id = Integer(index=False, store=True)
    v1_url = Text(index=False, store=True)
    race = Text(index=False, store=True)
    gender = Text(index=False, store=True)

    class Meta:
        doc_type = 'officer'
