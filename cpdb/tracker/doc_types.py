from elasticsearch_dsl import Integer, DocType, Text, Boolean

from .index_aliases import tracker_index_alias
from search.analyzers import autocomplete, autocomplete_search, text_analyzer, text_search_analyzer


@tracker_index_alias.doc_type
class AttachmentFileDocType(DocType):
    id = Integer()
    crid = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    title = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    text_content = Text(analyzer=text_analyzer, search_analyzer=text_search_analyzer)
    show = Boolean()

    class Meta:
        doc_type = 'attachment_file_doc_type'
