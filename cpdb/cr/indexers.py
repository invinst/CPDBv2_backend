from es_index import register_indexer
from es_index.indexers import BaseIndexer, PartialIndexer
from data.models import Allegation
from .doc_types import CRDocType
from .queries import AllegationQuery
from .index_aliases import cr_index_alias
from .serializers.cr_doc_serializers import AllegationSerializer

app_name = __name__.split('.')[0]


@register_indexer(app_name)
class CRIndexer(BaseIndexer):
    doc_type_klass = CRDocType
    index_alias = cr_index_alias
    serializer = AllegationSerializer()

    def get_queryset(self):
        return AllegationQuery().execute()

    def extract_datum(self, datum):
        return self.serializer.serialize(datum)


class CRPartialIndexer(PartialIndexer, CRIndexer):
    def get_postgres_count(self, keys):
        return Allegation.objects.filter(crid__in=keys).count()

    def get_batch_queryset(self, keys):
        return AllegationQuery().where(crid__in=keys).execute()

    def get_batch_update_docs_queries(self, keys):
        return self.doc_type_klass.search().query('terms', crid=keys)
