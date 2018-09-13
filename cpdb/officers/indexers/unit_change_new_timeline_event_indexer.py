from django.db.models import F

from es_index import register_indexer
from es_index.indexers import BaseIndexer
from data.models import OfficerHistory
from officers.index_aliases import officers_index_alias
from officers.doc_types import OfficerNewTimelineEventDocType
from officers.serializers.unit_change_new_timeline_serializer import UnitChangeNewTimelineSerializer
from officers.query_helpers.officer_rank_by_date import initialize_rank_by_date_helper, get_officer_rank_by_date

app_name = __name__.split('.')[0]


@register_indexer(app_name)
class UnitChangeNewTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerNewTimelineEventDocType
    index_alias = officers_index_alias
    serializer = UnitChangeNewTimelineSerializer()

    def get_queryset(self):
        initialize_rank_by_date_helper()
        return OfficerHistory.objects.filter(effective_date__isnull=False)\
            .exclude(effective_date=F('officer__appointed_date'))\
            .select_related('unit')

    def extract_datum(self, obj):
        datum = obj.__dict__
        datum['unit_name'] = getattr(obj.unit, 'unit_name', None)
        datum['unit_description'] = getattr(obj.unit, 'description', None)
        datum['rank'] = get_officer_rank_by_date(datum['officer_id'], datum['effective_date'])
        return self.serializer.serialize(datum)
