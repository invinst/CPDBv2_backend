from itertools import combinations

from django.db.models import F, Q

from tqdm import tqdm

from data import officer_percentile
from data.constants import (
    MIN_VISUAL_TOKEN_YEAR, MAX_VISUAL_TOKEN_YEAR,
    PERCENTILE_TRR_GROUP, PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP, PERCENTILE_ALLEGATION_GROUP
)
from data.models import Officer, OfficerAllegation, OfficerHistory, Allegation, Award
from es_index import register_indexer
from es_index.indexers import BaseIndexer
from officers.serializers.doc_serializers import (
    OfficerYearlyPercentileSerializer,
    OfficerInfoSerializer,
)
from trr.models import TRR
from .doc_types import (
    OfficerSocialGraphDocType,
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
)

app_name = __name__.split('.')[0]


@register_indexer(app_name)
class OfficersIndexer(BaseIndexer):
    doc_type_klass = OfficerInfoDocType
    index_alias = officers_index_alias

    def __init__(self):
        super(OfficersIndexer, self).__init__()
        top_percentile = officer_percentile.top_percentile(percentile_groups=[PERCENTILE_ALLEGATION_GROUP])
        self.top_percentile_dict = {officer.id: officer for officer in top_percentile}

    def get_queryset(self):
        return Officer.objects.all()

    def extract_datum(self, datum):
        if datum.id in self.top_percentile_dict:
            setattr(datum, 'percentile_allegation', self.top_percentile_dict[datum.id].percentile_allegation)
        return OfficerInfoSerializer(datum).data


@register_indexer(app_name)
class SocialGraphIndexer(BaseIndexer):
    doc_type_klass = OfficerSocialGraphDocType
    index_alias = officers_index_alias

    def get_queryset(self):
        return Officer.objects.all()

    def _cr_years(self, officer):
        dates = officer.officerallegation_set.values_list('allegation__incident_date', flat=True)
        return sorted([_date.year if _date is not None else None for _date in dates])

    def _node(self, officer):
        return {
            "id": officer.id,
            "name": officer.full_name,
            "cr_years": self._cr_years(officer)
        }

    def _links(self, officers):
        links = []
        for o1, o2 in combinations(officers, 2):
            qs = Allegation.objects.filter(officerallegation__officer=o1) \
                .filter(officerallegation__officer=o2).distinct()
            if qs.exists():
                link = {
                    'source': o1.id,
                    'target': o2.id,
                    'cr_years': sorted([
                        _date.year if _date is not None else None
                        for _date in qs.values_list('incident_date', flat=True)
                    ])
                }
                links.append(link)
        return links

    def extract_datum(self, officer):
        coaccuseds = Officer.objects.filter(
            officerallegation__allegation__officerallegation__officer=officer).distinct().order_by('id')

        return {'officer_id': officer.pk, 'graph': {
            'links': self._links(coaccuseds),
            'nodes': [self._node(coaccused) for coaccused in coaccuseds]
        }}


@register_indexer(app_name)
class OfficerPercentileIndexer(BaseIndexer):
    index_alias = officers_index_alias
    doc_type_klass = OfficerInfoDocType
    parent_doc_type_property = 'percentiles'
    percentile_groups = [
        PERCENTILE_ALLEGATION_GROUP,
        PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP,
        PERCENTILE_TRR_GROUP
    ]

    def get_queryset(self):
        def _not_retired(officer):
            return not officer.resignation_date or officer.year <= officer.resignation_date.year

        results = []
        for yr in tqdm(range(MIN_VISUAL_TOKEN_YEAR, MAX_VISUAL_TOKEN_YEAR + 1), desc='Prepare percentile data'):
            officers = officer_percentile.top_percentile(yr, percentile_groups=self.percentile_groups)
            results.extend(filter(_not_retired, officers))
        return results

    def extract_datum(self, datum):
        return OfficerYearlyPercentileSerializer(datum).data


@register_indexer(app_name)
class CRNewTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerNewTimelineEventDocType
    index_alias = officers_index_alias

    def get_queryset(self):
        return OfficerAllegation.objects.filter(start_date__isnull=False)

    def extract_datum(self, datum):
        return CRNewTimelineSerializer(datum).data


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
