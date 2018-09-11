from django.db import models

from es_index import register_indexer
from es_index.utils import timing_validate
from es_index.indexers import BaseIndexer, PartialIndexer
from data.models import Allegation, PoliceWitness, OfficerAllegation
from .doc_types import CRDocType
from .queries import AllegationQuery, CoaccusedQuery, InvestigatorAllegationQuery
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
        sustained_count = OfficerAllegation.objects.filter(
            officer=models.OuterRef('officer_id')
        )
        queryset = PoliceWitness.objects.all().select_related('officer')\
            .annotate(allegation_count=models.Count('officer__officerallegation'))\
            .annotate(sustained_count=models.Count(models.Subquery(sustained_count.values('id')[:1])))
        for obj in queryset.values(
                'officer_id', 'allegation_id', 'officer__first_name', 'officer__last_name',
                'officer__middle_initial', 'officer__middle_initial2', 'officer__suffix_name',
                'officer__complaint_percentile', 'officer__civilian_allegation_percentile',
                'officer__internal_allegation_percentile', 'officer__trr_percentile',
                'officer__gender', 'officer__race', 'allegation_count', 'sustained_count'):
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
