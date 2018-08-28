from datetime import datetime

from es_index import register_indexer
from es_index.indexers import BaseIndexer
from data.constants import GENDER_DICT, FINDINGS_DICT
from .doc_types import CRDocType
from .queries import AllegationQuery
from .index_aliases import cr_index_alias
from .serializers.cr_doc_serializers import AllegationSerializer

app_name = __name__.split('.')[0]


@register_indexer(app_name)
class CRIndexer(BaseIndexer):
    doc_type_klass = CRDocType
    index_alias = cr_index_alias
    query = AllegationQuery()
    serializer = AllegationSerializer()

    def __init__(self, query=None, *args, **kwargs):
        super(CRIndexer, self).__init__(*args, **kwargs)
        if query is not None:
            self.query = query

    def get_queryset(self):
        return self.query.execute()

    def extract_datum(self, datum):
        return self.serializer.serialize(datum)
