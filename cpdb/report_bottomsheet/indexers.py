from es_index import register_indexer
from es_index.indexers import BaseIndexer
from data.models import Officer
from .doc_types import OfficerDocType
from .serializers import OfficerSerializer


@register_indexer
class OfficerIndexer(BaseIndexer):
    doc_type_klass = OfficerDocType

    def get_queryset(self):
        return Officer.objects.all()

    def extract_datum(self, datum):
        return OfficerSerializer(datum).data
