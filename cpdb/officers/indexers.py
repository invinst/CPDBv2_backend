from itertools import combinations

from django.db.models import F, Q
from django.utils.timezone import now

from tqdm import tqdm

from data.models import Officer, OfficerAllegation, OfficerHistory, Allegation, Award
from data.utils.calculations import calculate_top_percentile
from es_index import register_indexer
from es_index.indexers import BaseIndexer
from officers.serializers.doc_serializers import (
    OfficerYearlyPercentileSerializer,
    OfficerInfoSerializer,
    OfficerSinglePercentileSerializer,
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

    def get_queryset(self):
        return Officer.objects.all()

    def extract_datum(self, datum):
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

    def get_queryset(self):
        results = []
        for yr in tqdm(range(2001, now().year + 1), desc='Prepare percentile data'):
            officers = Officer.top_complaint_officers(100, yr)
            if officers and officers[0].year < yr:
                # we have no more data to calculate, should break here
                break
            results.extend(officers)
        return results

    def extract_datum(self, datum):
        return OfficerYearlyPercentileSerializer(datum).data


@register_indexer(app_name)
class OfficerSinglePercentileIndexer(BaseIndexer):
    index_alias = officers_index_alias
    doc_type_klass = OfficerInfoDocType
    op_type = 'update'

    def get_queryset(self):
        return Officer.annotate_honorable_mention_percentile_officers()

    def extract_datum(self, datum):
        return OfficerSinglePercentileSerializer(datum).data


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

    def __init__(self, *args, **kwargs):
        super(OfficerCoaccusalsIndexer, self).__init__(*args, **kwargs)
        self.top_percentile_dict = calculate_top_percentile()

    def get_queryset(self):
        return Officer.objects.all()

    def extract_datum(self, officer):
        result = OfficerCoaccusalsSerializer(officer).data
        for coaccusals in result['coaccusals']:
            try:
                coaccusals.update(self.top_percentile_dict[coaccusals['id']])
            except KeyError:
                pass

        return result
