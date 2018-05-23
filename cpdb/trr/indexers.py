from es_index import register_indexer
from es_index.indexers import BaseIndexer
from data.models import Officer
from data.constants import PERCENTILE_ALLEGATION_INTERNAL, PERCENTILE_ALLEGATION_CIVILIAN, PERCENTILE_TRR
from trr.models import TRR
from .doc_types import TRRDocType
from .index_aliases import trr_index_alias
from .serializers.trr_doc_serializers import TRRDocSerializer


app_name = __name__.split('.')[0]


@register_indexer(app_name)
class TRRIndexer(BaseIndexer):
    doc_type_klass = TRRDocType
    index_alias = trr_index_alias

    def __init__(self, *args, **kwargs):
        super(TRRIndexer, self).__init__(*args, **kwargs)
        percentile_types = [PERCENTILE_ALLEGATION_INTERNAL, PERCENTILE_ALLEGATION_CIVILIAN, PERCENTILE_TRR]

        top_percentile = Officer.top_complaint_officers(100, percentile_types=percentile_types)

        self.top_percentile_dict = {
            data.officer_id: {
                'percentile_allegation_civilian': data.percentile_allegation_civilian,
                'percentile_allegation_internal': data.percentile_allegation_internal,
                'percentile_trr': data.percentile_trr,
            }
            for data in top_percentile
        }

    def get_queryset(self):
        return TRR.objects.all()

    def extract_datum(self, datum):
        result = TRRDocSerializer(datum).data

        officer = result['officer']
        if officer:
            try:
                officer.update(self.top_percentile_dict[officer['id']])
            except KeyError:
                pass

        return result
