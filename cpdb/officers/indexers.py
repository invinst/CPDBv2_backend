import itertools

from django.db.models import F, Q

from data import officer_percentile
from data.constants import (
    MIN_VISUAL_TOKEN_YEAR, MAX_VISUAL_TOKEN_YEAR,
    PERCENTILE_TRR_GROUP, PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP, PERCENTILE_ALLEGATION_GROUP
)
from data.models import Officer, OfficerAllegation, OfficerHistory, Award, Salary
from es_index import register_indexer
from es_index.utils import timing_validate
from es_index.indexers import BaseIndexer, PartialIndexer
from es_index.serializers import get_gender, get_age_range
from trr.models import TRR
from .doc_types import (
    OfficerNewTimelineEventDocType,
    OfficerInfoDocType,
    OfficerCoaccusalsDocType,
)
from .index_aliases import officers_index_alias
from officers.serializers.doc_serializers import (
    CRNewTimelineSerializer,
    UnitChangeNewTimelineSerializer,
    JoinedNewTimelineSerializer,
    AwardNewTimelineSerializer,
    TRRNewTimelineSerializer,
    OfficerCoaccusalsSerializer,
    OfficerSerializer,
    RankChangeNewTimelineSerializer
)
from .queries import OfficerQuery, AllegationQuery, AwardQuery

app_name = __name__.split('.')[0]


@register_indexer(app_name)
class OfficersIndexer(BaseIndexer):
    doc_type_klass = OfficerInfoDocType
    index_alias = officers_index_alias
    serializer = OfficerSerializer()
    percentile_groups = [
        PERCENTILE_ALLEGATION_GROUP,
        PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP,
        PERCENTILE_TRR_GROUP
    ]

    def __init__(self):
        super(OfficersIndexer, self).__init__()
        self.populate_top_percentile_dict()
        self.populate_allegation_dict()
        self.populate_award_dict()

    @timing_validate('OfficersIndexer: Preparing percentile data...')
    def populate_top_percentile_dict(self):
        self.yearly_top_percentile = dict()
        for yr in range(MIN_VISUAL_TOKEN_YEAR, MAX_VISUAL_TOKEN_YEAR + 1):
            for officer in officer_percentile.top_percentile(yr, percentile_groups=self.percentile_groups):
                if officer.resignation_date and yr > officer.resignation_date.year:
                    continue
                officer_list = self.yearly_top_percentile.setdefault(officer.id, [])
                officer_dict = {
                    'id': officer.id,
                    'year': yr
                }
                for attr in [
                        'percentile_trr',
                        'percentile_allegation',
                        'percentile_allegation_civilian',
                        'percentile_allegation_internal']:
                    if hasattr(officer, attr):
                        officer_dict[attr] = str(round(getattr(officer, attr), 4))
                officer_list.append(officer_dict)

    @timing_validate('OfficersIndexer: Populating allegation dict...')
    def populate_allegation_dict(self):
        allegations = AllegationQuery().execute()
        self.allegation_dict = dict()
        self.coaccusals = dict()
        transform_gender = get_gender('gender', 'Unknown')
        transform_age = get_age_range([20, 30, 40, 50], 'age', 'Unknown')
        for allegation in allegations:
            for complainant in allegation['complainants']:
                complainant['gender'] = transform_gender(complainant)
                complainant['age'] = transform_age(complainant)
                if complainant['race'] == '':
                    complainant['race'] = 'Unknown'
            for complaint in allegation['complaints']:
                self.allegation_dict.setdefault(complaint['officer_id'], []).append(allegation)
            for complaint_a, complaint_b in itertools.combinations(allegation['complaints'], 2):
                officer_id_a = complaint_a['officer_id']
                officer_id_b = complaint_b['officer_id']
                dict_a = self.coaccusals.setdefault(officer_id_a, dict())
                dict_a[officer_id_b] = dict_a.get(officer_id_b, 0) + 1
                dict_b = self.coaccusals.setdefault(officer_id_b, dict())
                dict_b[officer_id_a] = dict_b.get(officer_id_a, 0) + 1

    @timing_validate('OfficersIndexer: Populating award dict...')
    def populate_award_dict(self):
        self.award_dict = dict()
        awards = AwardQuery().execute()
        for award in awards:
            self.award_dict.setdefault(award['officer_id'], []).append(award)

    def get_queryset(self):
        return Officer.objects.all()

    def get_query(self):
        return OfficerQuery().execute()

    def extract_datum(self, datum):
        datum['allegations'] = self.allegation_dict.get(datum['id'], [])
        datum['awards'] = self.award_dict.get(datum['id'], [])
        datum['coaccusals'] = self.coaccusals.get(datum['id'], dict())
        datum['percentiles'] = self.yearly_top_percentile.get(datum['id'], [])
        return self.serializer.serialize(datum)


@register_indexer(app_name)
class CRNewTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerNewTimelineEventDocType
    index_alias = officers_index_alias

    def get_queryset(self):
        return OfficerAllegation.objects.filter(start_date__isnull=False)

    def extract_datum(self, datum):
        return CRNewTimelineSerializer(datum).data


class CRNewTimelineEventPartialIndexer(PartialIndexer, CRNewTimelineEventIndexer):
    def get_batch_queryset(self, keys):
        return OfficerAllegation.objects.filter(
            start_date__isnull=False,
            allegation__crid__in=keys)

    def get_postgres_count(self, keys):
        return self.get_batch_queryset(keys).count()

    def get_batch_update_docs_queries(self, keys):
        return self.doc_type_klass.search().query('terms', crid=keys).filter('term', kind='CR')


@register_indexer(app_name)
class UnitChangeNewTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerNewTimelineEventDocType
    index_alias = officers_index_alias

    def get_queryset(self):
        return OfficerHistory.objects.filter(
            effective_date__isnull=False,
        ).exclude(
            effective_date=F('officer__appointed_date'),
        )

    def extract_datum(self, datum):
        return UnitChangeNewTimelineSerializer(datum).data


@register_indexer(app_name)
class RankChangeNewTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerNewTimelineEventDocType
    index_alias = officers_index_alias

    def get_queryset(self):
        return Salary.objects.rank_histories_without_joined()

    def extract_datum(self, datum):
        return RankChangeNewTimelineSerializer(datum).data


@register_indexer(app_name)
class JoinedNewTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerNewTimelineEventDocType
    index_alias = officers_index_alias

    def get_queryset(self):
        return Officer.objects.filter(appointed_date__isnull=False)

    def extract_datum(self, officer):
        return JoinedNewTimelineSerializer(officer).data


@register_indexer(app_name)
class AwardNewTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerNewTimelineEventDocType
    index_alias = officers_index_alias

    def get_queryset(self):
        return Award.objects.filter(
            Q(start_date__isnull=False),
            ~Q(award_type__contains='Honorable Mention'),
            ~Q(award_type__in=['Complimentary Letter', 'Department Commendation'])
        )

    def extract_datum(self, awards):
        return AwardNewTimelineSerializer(awards).data


@register_indexer(app_name)
class TRRNewTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerNewTimelineEventDocType
    index_alias = officers_index_alias

    def get_queryset(self):
        return TRR.objects.filter(officer__isnull=False)

    def extract_datum(self, trrs):
        return TRRNewTimelineSerializer(trrs).data


@register_indexer(app_name)
class OfficerCoaccusalsIndexer(BaseIndexer):
    doc_type_klass = OfficerCoaccusalsDocType
    index_alias = officers_index_alias

    def get_queryset(self):
        return Officer.objects.all()

    def extract_datum(self, officer):
        return OfficerCoaccusalsSerializer(officer).data
