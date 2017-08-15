from es_index import register_indexer
from es_index.indexers import BaseIndexer
from data.models import Allegation
from .doc_types import CRDocType
from .index_aliases import cr_index_alias
from .serializers import CRSerializer


app_name = __name__.split('.')[0]


@register_indexer(app_name)
class CRIndexer(BaseIndexer):
    doc_type_klass = CRDocType
    index_alias = cr_index_alias

    def get_queryset(self):
        return Allegation.objects.all()

    def extract_datum(self, datum):
        return CRSerializer(datum).data
