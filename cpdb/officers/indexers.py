from datetime import date

from es_index import register_indexer
from es_index.indexers import BaseIndexer
from data.models import Officer, OfficerAllegation, OfficerHistory
from .doc_types import OfficerSummaryDocType, OfficerTimelineEventDocType, OfficerTimelineMinimapDocType
from .serializers import (
    OfficerSummarySerializer, CRTimelineSerializer, UnitChangeTimelineSerializer, JoinedTimelineSerializer
)


@register_indexer
class OfficersIndexer(BaseIndexer):
    doc_type_klass = OfficerSummaryDocType

    def get_queryset(self):
        return Officer.objects.all()

    def extract_datum(self, datum):
        return OfficerSummarySerializer(datum).data


@register_indexer
class CRTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerTimelineEventDocType

    def get_queryset(self):
        return OfficerAllegation.objects.filter(start_date__isnull=False)

    def extract_datum(self, datum):
        return CRTimelineSerializer(datum).data


@register_indexer
class UnitChangeTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerTimelineEventDocType

    def get_queryset(self):
        return OfficerHistory.objects.filter(effective_date__isnull=False)

    def extract_datum(self, datum):
        return UnitChangeTimelineSerializer(datum).data


@register_indexer
class YearTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerTimelineEventDocType

    def get_queryset(self):
        return Officer.objects.all()

    def extract_datum(self, officer):
        results = dict()
        for oa in OfficerAllegation.objects.filter(officer=officer, start_date__isnull=False):
            year_dict = results.setdefault(oa.start_date.year, dict())
            year_dict.setdefault('crs', 0)
            year_dict['crs'] += 1

        if officer.appointed_date is not None:
            year_dict = results.setdefault(officer.appointed_date.year, dict())
            year_dict.setdefault('crs', 0)

        for oh in OfficerHistory.objects.filter(officer=officer, effective_date__isnull=False):
            year_dict = results.setdefault(oh.effective_date.year, dict())
            year_dict.setdefault('crs', 0)

        for key, val in results.iteritems():
            val.update(
                {
                    'kind': 'YEAR',
                    'officer_id': officer.pk,
                    'year': key,
                    'priority_sort': 20,
                    'date_sort': date(key, 12, 31),
                    'year_sort': key
                }
            )
            yield val


@register_indexer
class JoinedTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerTimelineEventDocType

    def get_queryset(self):
        return Officer.objects.filter(appointed_date__isnull=False)

    def extract_datum(self, officer):
        return JoinedTimelineSerializer(officer).data


@register_indexer
class TimelineMinimapIndexer(BaseIndexer):
    doc_type_klass = OfficerTimelineMinimapDocType

    def get_queryset(self):
        return Officer.objects.all()

    def extract_datum(self, officer):
        items = []
        for oa in OfficerAllegation.objects.filter(start_date__isnull=False, officer=officer):
            items.append({'kind': 'CR', 'year': oa.start_date.year, 'date': oa.start_date})

        for oh in OfficerHistory.objects.filter(effective_date__isnull=False, officer=officer):
            items.append({'kind': 'Unit', 'year': oh.effective_date.year, 'date': oh.effective_date})

        if officer.appointed_date is not None:
            items.append({'kind': 'Joined', 'year': officer.appointed_date.year, 'date': officer.appointed_date})

        items = sorted(items, key=lambda item: item['date'], reverse=True)
        for item in items:
            item.pop('date')

        return {'officer_id': officer.pk, 'items': items}
