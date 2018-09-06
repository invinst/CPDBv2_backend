from data.models import Allegation
from es_index import register_indexer
from es_index.indexers import BaseIndexer, PartialIndexer
from .doc_types import CRDocType
from .index_aliases import cr_index_alias
from .serializers.cr_doc_serializer import CRDocSerializer

app_name = __name__.split('.')[0]


@register_indexer(app_name)
class CRIndexer(BaseIndexer):
    doc_type_klass = CRDocType
    index_alias = cr_index_alias

    def get_queryset(self):
        return Allegation.objects.all()

    def extract_datum(self, datum):
        return CRDocSerializer(datum).data


class CRPartialIndexer(PartialIndexer, CRIndexer):
    def get_batch_querysets(self, keys):
        return Allegation.objects.filter(crid__in=keys)

    def get_batch_update_docs_queries(self, keys):
        return self.doc_type_klass.search().query('terms', crid=keys)
