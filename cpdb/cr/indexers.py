from es_index import register_indexer
from es_index.utils import timing_validate
from es_index.indexers import BaseIndexer, PartialIndexer
from data.models import Allegation
from .doc_types import CRDocType
from .queries import AllegationQuery, CoaccusedQuery, InvestigatorAllegationQuery, PoliceWitnessQuery
from .index_aliases import cr_index_alias
from .serializers.cr_doc_serializers import AllegationSerializer

app_name = __name__.split('.')[0]


@register_indexer(app_name)
class CRIndexer(BaseIndexer):
    doc_type_klass = CRDocType
    index_alias = cr_index_alias
    serializer = AllegationSerializer()

    def __init__(self, *args, **kwargs):
        super(CRIndexer, self).__init__(*args, **kwargs)
        self.populate_policewitness_dict()
        self.populate_coaccused_dict()
        self.populate_investigator_dict()

    @timing_validate('CRIndexer: Populating policewitness dict...')
    def populate_policewitness_dict(self):
        self.policewitness_dict = dict()
        for obj in PoliceWitnessQuery().execute():
            self.policewitness_dict.setdefault(obj['allegation_id'], []).append(obj)

    @timing_validate('CRIndexer: Populating coaccused dict...')
    def populate_coaccused_dict(self):
        self.coaccused_dict = dict()
        for obj in CoaccusedQuery().execute():
            self.coaccused_dict.setdefault(obj['allegation_id'], []).append(obj)

    @timing_validate('CRIndexer: Populating investigator dict...')
    def populate_investigator_dict(self):
        self.investigator_dict = dict()
        for obj in InvestigatorAllegationQuery().execute():
            self.investigator_dict.setdefault(obj['allegation_id'], []).append(obj)

    def get_queryset(self):
        return AllegationQuery().execute()

    def extract_datum(self, datum):
        datum['coaccused'] = self.coaccused_dict.get(datum['id'], [])
        datum['investigators'] = self.investigator_dict.get(datum['id'], [])
        datum['police_witnesses'] = self.policewitness_dict.get(datum['id'], [])

        return self.serializer.serialize(datum)


class CRPartialIndexer(PartialIndexer, CRIndexer):
    def get_postgres_count(self, keys):
        return Allegation.objects.filter(crid__in=keys).count()

    def get_batch_queryset(self, keys):
        return AllegationQuery().where(crid__in=keys).execute()

    def get_batch_update_docs_queries(self, keys):
        return self.doc_type_klass.search().query('terms', crid=keys)
