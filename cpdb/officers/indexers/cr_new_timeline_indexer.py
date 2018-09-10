from sortedcontainers import SortedKeyList

from data.models import Salary, OfficerAllegation
from es_index import register_indexer
from es_index.indexers import BaseIndexer, PartialIndexer
from officers.doc_types import OfficerNewTimelineEventDocType
from officers.index_aliases import officers_index_alias
from officers.serializers.cr_new_timeline_serializer import CRNewTimelineSerializer
from officers.queries import (
    OfficerHistoryQuery, CRTimelineQuery, AllegationTimelineQuery
)

app_name = __name__.split('.')[0]


@register_indexer(app_name)
class CRNewTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerNewTimelineEventDocType
    index_alias = officers_index_alias
    serializer = CRNewTimelineSerializer()

    def history_sort_key(self, obj):
        return obj['effective_date']

    def rank_sort_key(self, obj):
        return obj['spp_date']

    def __init__(self, *args, **kwargs):
        super(CRNewTimelineEventIndexer, self).__init__(*args, **kwargs)

        self.officer_history_dict = dict()
        for officer_history in OfficerHistoryQuery().execute():
            history_list = self.officer_history_dict.setdefault(
                officer_history['officer_id'],
                SortedKeyList(key=self.history_sort_key))
            history_list.add(officer_history)

        self.rank_dict = dict()
        for rank in Salary.objects.all().values('officer_id', 'spp_date', 'rank'):
            rank_list = self.rank_dict.setdefault(
                rank['officer_id'],
                SortedKeyList(key=self.rank_sort_key))
            rank_list.add(rank)

        self.allegation_dict = {
            allegation['id']: allegation
            for allegation in AllegationTimelineQuery().execute()
        }

    def get_queryset(self):
        return OfficerAllegation.objects.filter(start_date__isnull=False)

    def get_query(self):
        return CRTimelineQuery().where(start_date__isnull=False).execute()

    def extract_datum(self, datum):
        officer_id = datum['officer_id']
        if officer_id in self.rank_dict:
            rank_list = self.rank_dict[officer_id]
            ind = rank_list.bisect_key_right(datum['start_date'])
            if ind > 0:
                datum['rank'] = rank_list[ind-1]['rank']

        if officer_id in self.officer_history_dict:
            history_list = self.officer_history_dict[officer_id]
            ind = history_list.bisect_key_right(datum['start_date'])
            if ind > 0:
                history = history_list[ind-1]
                if history['end_date'] is None or history['end_date'] >= datum['start_date']:
                    datum['unit_name'] = history['unit_name']
                    datum['unit_description'] = history['description']

        allegation = self.allegation_dict[datum['allegation_id']]
        datum['crid'] = allegation['crid']
        datum['coaccused_count'] = allegation['coaccused_count']
        datum['point'] = allegation['point']
        datum['victims'] = allegation['victims']
        datum['attachments'] = allegation['attachments']

        return self.serializer.serialize(datum)


class CRNewTimelineEventPartialIndexer(PartialIndexer, CRNewTimelineEventIndexer):
    def get_batch_queryset(self, keys):
        return OfficerAllegation.objects.filter(
            start_date__isnull=False,
            allegation__crid__in=keys)

    def get_postgres_count(self, keys):
        return self.get_batch_queryset(keys).count()

    def get_batch_update_docs_queries(self, keys):
        return self.doc_type_klass.search().query('terms', crid=keys).filter('term', kind='CR')
