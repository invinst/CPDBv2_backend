from django.db.models import F

from sortedcontainers import SortedKeyList

from es_index import register_indexer
from es_index.indexers import BaseIndexer
from es_index.utils import timing_validate
from data.models import OfficerHistory, Salary
from officers.index_aliases import officers_index_alias
from officers.doc_types import OfficerNewTimelineEventDocType
from officers.serializers.unit_change_new_timeline_serializer import UnitChangeNewTimelineSerializer

app_name = __name__.split('.')[0]


@register_indexer(app_name)
class UnitChangeNewTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerNewTimelineEventDocType
    index_alias = officers_index_alias
    serializer = UnitChangeNewTimelineSerializer()

    @timing_validate('UnitChangeNewTimelineEventIndexer: Populating rank dict...')
    def _populate_rank_dict(self):
        if hasattr(self, '_rank_dict'):
            return
        self._rank_dict = dict()
        for rank in Salary.objects.filter(spp_date__isnull=False).values('officer_id', 'spp_date', 'rank'):
            rank_list = self._rank_dict.setdefault(
                rank['officer_id'],
                SortedKeyList(key=lambda o: o['spp_date']))
            rank_list.add(rank)

    def get_queryset(self):
        self._populate_rank_dict()
        return OfficerHistory.objects.filter(effective_date__isnull=False)\
            .exclude(effective_date=F('officer__appointed_date'))\
            .select_related('unit')

    def extract_datum(self, obj):
        datum = obj.__dict__
        datum['unit_name'] = getattr(obj.unit, 'unit_name', None)
        datum['unit_description'] = getattr(obj.unit, 'description', None)
        officer_id = datum['officer_id']
        if officer_id in self._rank_dict:
            rank_list = self._rank_dict[officer_id]
            ind = rank_list.bisect_key_right(datum['effective_date'])
            if ind > 0:
                datum['rank'] = rank_list[ind-1]['rank']
        return self.serializer.serialize(datum)
