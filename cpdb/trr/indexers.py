from es_index import register_indexer
from es_index.indexers import BaseIndexer
from trr.models import TRR
from .doc_types import TRRDocType
from .index_aliases import trr_index_alias
from .serializers.trr_doc_serializers import TRRDocSerializer


app_name = __name__.split('.')[0]


@register_indexer(app_name)
class TRRIndexer(BaseIndexer):
    doc_type_klass = TRRDocType
    index_alias = trr_index_alias

    def get_queryset(self):
        return TRR.objects.all()

    def extract_datum(self, datum):
        return TRRDocSerializer(datum).data
