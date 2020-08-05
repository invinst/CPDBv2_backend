from es_index import register_indexer
from es_index.indexers import BaseIndexer
from data.models import AttachmentFile
from .doc_types import AttachmentFileDocType
from .index_aliases import tracker_index_alias

app_name = __name__.split('.')[0]


@register_indexer(app_name)
class AttachmentFileIndexer(BaseIndexer):
    doc_type_klass = AttachmentFileDocType
    index_alias = tracker_index_alias

    def get_queryset(self):
        return AttachmentFile.objects.all()

    def extract_datum(self, datum):
        return {
            'id': datum.id,
            'crid': datum.owner_id,
            'title': datum.title,
            'text_content': datum.text_content,
            'show': datum.show,
        }
