from es_index import register_indexer
from es_index.indexers import BaseIndexer
from data import officer_percentile
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
        top_percentile = officer_percentile.top_visual_token_percentile()

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

        try:
            result['officer'].update(self.top_percentile_dict[result['officer']['id']])
        except (AttributeError, KeyError):
            pass

        return result
