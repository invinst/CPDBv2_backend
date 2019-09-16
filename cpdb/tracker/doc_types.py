from elasticsearch_dsl import Integer, DocType, Text, Boolean

from .index_aliases import tracker_index_alias
from search.analyzers import autocomplete, autocomplete_search


@tracker_index_alias.doc_type
class AttachmentFileDocType(DocType):
    id = Integer()
    crid = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    title = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    text_content = Text(analyzer=autocomplete, search_analyzer=autocomplete_search)
    show = Boolean()

    class Meta:
        doc_type = 'attachment_file_doc_type'
