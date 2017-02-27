from es_index import register_indexer
from es_index.indexers import BaseIndexer
from data.models import Officer
from .doc_types import OfficerSummaryDocType
from .serializers import OfficerSummarySerializer


@register_indexer
class OfficersIndexer(BaseIndexer):
    doc_type_klass = OfficerSummaryDocType

    def get_queryset(self):
        return Officer.objects.all()

    def extract_datum(self, datum):
        return OfficerSummarySerializer(datum).data
