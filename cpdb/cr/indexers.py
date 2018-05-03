from es_index import register_indexer
from es_index.indexers import BaseIndexer
from data.models import Allegation, Officer
from data.constants import PERCENTILE_TYPES
from .doc_types import CRDocType
from .index_aliases import cr_index_alias
from .serializers.cr_doc_serializer import CRDocSerializer


app_name = __name__.split('.')[0]


@register_indexer(app_name)
class CRIndexer(BaseIndexer):
    doc_type_klass = CRDocType
    index_alias = cr_index_alias

    def __init__(self, *args, **kwargs):
        super(CRIndexer, self).__init__(*args, **kwargs)
        top_percentile = Officer.top_complaint_officers(100, percentile_types=PERCENTILE_TYPES)
        self.top_percentile_dict = {
            data['officer_id']: {k: v for k, v in data.items() if k in [
                'percentile_allegation',
                'percentile_allegation_civilian',
                'percentile_allegation_internal',
                'percentile_trr'
            ]}
            for data in top_percentile
        }

    def get_queryset(self):
        return Allegation.objects.all()

    def extract_datum(self, datum):
        result = CRDocSerializer(datum).data
        for coaccused in result['coaccused']:
            try:
                coaccused.update(self.top_percentile_dict[coaccused['id']])
            except KeyError:  # pragma: no cover
                pass

        for involvement in result['involvements']:
            try:
                involvement.update(self.top_percentile_dict[involvement['officer_id']])
            except KeyError:  # pragma: no cover
                pass

        return result
