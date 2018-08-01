from data.models import Allegation
from data.utils.calculations import calculate_top_percentile
from es_index import register_indexer
from es_index.indexers import BaseIndexer
from .doc_types import CRDocType
from .index_aliases import cr_index_alias
from .serializers.cr_doc_serializer import CRDocSerializer

app_name = __name__.split('.')[0]


@register_indexer(app_name)
class CRIndexer(BaseIndexer):
    doc_type_klass = CRDocType
    index_alias = cr_index_alias

    def __init__(self, queryset=None, *args, **kwargs):
        super(CRIndexer, self).__init__(*args, **kwargs)
        self.queryset = queryset
        self.top_percentile_dict = calculate_top_percentile()

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        return Allegation.objects.all()

    def extract_datum(self, datum):
        result = CRDocSerializer(datum).data
        for coaccused in result['coaccused']:
            try:
                coaccused.update(self.top_percentile_dict[coaccused['id']])
            except KeyError:
                pass

        for involvement in result['involvements']:
            try:
                involvement.update(self.top_percentile_dict[involvement['officer_id']])
            except KeyError:
                pass

        return result
