from es_index import register_indexer
from es_index.indexers import BaseIndexer

from data.models import Officer
from .doc_types import OfficerDocType
from .index_aliases import twitterbot_index_alias
from .serializers import OfficerSerializer


app_name = __name__.split('.')[0]


@register_indexer(app_name)
class OfficerIndexer(BaseIndexer):
    doc_type_klass = OfficerDocType
    index_alias = twitterbot_index_alias

    def get_queryset(self):
        return Officer.objects.all()

    def extract_datum(self, datum):
        return OfficerSerializer(datum).data
