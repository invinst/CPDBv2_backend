from es_index import register_indexer
from es_index.indexers import BaseIndexer
from data.models import Allegation
from .doc_types import CRDocType
from .serializers import CRSerializer


@register_indexer
class CRIndexer(BaseIndexer):
    doc_type_klass = CRDocType

    def get_queryset(self):
        return Allegation.objects.all()

    def extract_datum(self, datum):
        return CRSerializer(datum).data
