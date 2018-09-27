from django.db import models

from es_index import register_indexer
from es_index.utils import timing_validate
from es_index.indexers import BaseIndexer, PartialIndexer
from data.models import (
    Allegation, PoliceWitness, OfficerAllegation, InvestigatorAllegation,
    AttachmentFile, Complainant, Victim
)
from data.utils.subqueries import SQCount
from .doc_types import CRDocType
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
        self.populate_attachments_dict()
        self.populate_complainants_dict()
        self.populate_victims_dict()

    @timing_validate('CRIndexer: Populating policewitness dict...')
    def populate_policewitness_dict(self):
        self.policewitness_dict = dict()
        sustained_count = OfficerAllegation.objects.filter(
            officer=models.OuterRef('officer_id'),
            final_finding='SU'
        )
        queryset = PoliceWitness.objects.all().select_related('officer')\
            .annotate(allegation_count=models.Count('officer__officerallegation'))\
            .annotate(sustained_count=SQCount(sustained_count.values('id')))
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
        sustained_count = OfficerAllegation.objects.filter(
            officer=models.OuterRef('officer_id'),
            final_finding='SU'
        )
        allegation_count = OfficerAllegation.objects.filter(
            officer=models.OuterRef('officer_id')
        )
        queryset = OfficerAllegation.objects.all().select_related('officer', 'allegation_category')\
            .annotate(allegation_count=SQCount(allegation_count.values('id')))\
            .annotate(sustained_count=SQCount(sustained_count.values('id')))\
            .values(
                'officer_id', 'officer__first_name', 'officer__last_name', 'officer__middle_initial',
                'officer__middle_initial2', 'officer__suffix_name', 'officer__gender', 'officer__race',
                'officer__birth_year', 'officer__rank', 'officer__complaint_percentile',
                'officer__civilian_allegation_percentile', 'officer__internal_allegation_percentile',
                'officer__trr_percentile', 'allegation_id', 'final_outcome', 'final_finding',
                'recc_outcome', 'start_date', 'end_date', 'disciplined', 'allegation_count',
                'sustained_count', 'allegation_category__allegation_name', 'allegation_category__category',
                'allegation_category_id',
            )
        for obj in queryset:
            self.coaccused_dict.setdefault(obj['allegation_id'], []).append(obj)

    @timing_validate('CRIndexer: Populating investigator dict...')
    def populate_investigator_dict(self):
        self.investigator_dict = dict()
        num_cases = InvestigatorAllegation.objects.filter(investigator=models.OuterRef('investigator_id'))
        queryset = InvestigatorAllegation.objects.all().select_related('investigator__officer')\
            .annotate(num_cases=SQCount(num_cases.values('id'))).values(
                'investigator__officer_id', 'allegation_id', 'current_rank', 'investigator__first_name',
                'investigator__last_name', 'investigator__officer__first_name',
                'investigator__officer__last_name', 'investigator__officer__middle_initial',
                'investigator__officer__middle_initial2', 'investigator__officer__suffix_name',
                'investigator__officer__complaint_percentile', 'investigator__officer__civilian_allegation_percentile',
                'investigator__officer__internal_allegation_percentile', 'investigator__officer__trr_percentile',
                'num_cases')
        for obj in queryset:
            self.investigator_dict.setdefault(obj['allegation_id'], []).append(obj)

    @timing_validate('CRIndexer: Populating attachments dict...')
    def populate_attachments_dict(self):
        self.attachments_dict = dict()
        queryset = AttachmentFile.objects.all().values(
            'allegation_id', 'title', 'url', 'preview_image_url', 'file_type',
        )
        for obj in queryset:
            self.attachments_dict.setdefault(obj['allegation_id'], []).append(obj)

    @timing_validate('CRIndexer: Populating complainants dict...')
    def populate_complainants_dict(self):
        self.complainants_dict = dict()
        queryset = Complainant.objects.all().values(
            'allegation_id', 'race', 'gender', 'age'
        )
        for obj in queryset:
            self.complainants_dict.setdefault(obj['allegation_id'], []).append(obj)

    @timing_validate('CRIndexer: Populating victims dict...')
    def populate_victims_dict(self):
        self.victims_dict = dict()
        queryset = Victim.objects.all().values(
            'allegation_id', 'race', 'gender', 'age'
        )
        for obj in queryset:
            self.victims_dict.setdefault(obj['allegation_id'], []).append(obj)

    def get_queryset(self):
        # Values are extracted so that we can save some 2.5Gb of memory during run
        return Allegation.objects.all().select_related('beat').values(
            'crid', 'id', 'beat__name', 'summary', 'point', 'incident_date',
            'old_complaint_address', 'add1', 'add2', 'city', 'location'
        )

    def extract_datum(self, datum):
        datum['coaccused'] = self.coaccused_dict.get(datum['id'], [])
        datum['investigators'] = self.investigator_dict.get(datum['id'], [])
        datum['police_witnesses'] = self.policewitness_dict.get(datum['id'], [])
        datum['attachments'] = self.attachments_dict.get(datum['id'], [])
        datum['complainants'] = self.complainants_dict.get(datum['id'], [])
        datum['victims'] = self.victims_dict.get(datum['id'], [])

        return self.serializer.serialize(datum)


class CRPartialIndexer(PartialIndexer, CRIndexer):
    def get_batch_queryset(self, keys):
        return Allegation.objects.filter(crid__in=keys).select_related('beat').values(
            'crid', 'id', 'beat__name', 'summary', 'point', 'incident_date',
            'old_complaint_address', 'add1', 'add2', 'city', 'location'
        )

    def get_batch_update_docs_queries(self, keys):
        return self.doc_type_klass.search().query('terms', crid=keys)
