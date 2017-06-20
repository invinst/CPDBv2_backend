from data.models import PoliceUnit
from es_index.indexers import BaseIndexer
from .doc_types import UnitDocType
from es_index import register_indexer
from .serializers import UnitSummarySerializer
from .index_aliases import units_index_alias


app_name = __name__.split('.')[0]


@register_indexer(app_name)
class UnitIndexer(BaseIndexer):
    doc_type_klass = UnitDocType
    index_alias = units_index_alias

    def get_queryset(self):
        return PoliceUnit.objects.all()

    def extract_datum(self, datum):
        return UnitSummarySerializer(datum).data
