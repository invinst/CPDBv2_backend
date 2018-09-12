from django.db import models

from sortedcontainers import SortedKeyList

from data.models import (
    Salary, OfficerAllegation, OfficerHistory, AttachmentFile, Victim, Allegation
)
from es_index import register_indexer
from es_index.indexers import BaseIndexer, PartialIndexer
from es_index.utils import timing_validate
from officers.doc_types import OfficerNewTimelineEventDocType
from officers.index_aliases import officers_index_alias
from officers.serializers.cr_new_timeline_serializer import CRNewTimelineSerializer

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

    @timing_validate('CRNewTimelineEventIndexer: Populating officer history dict...')
    def _populate_officer_history_dict(self):
        if hasattr(self, '_officer_history_dict'):
            return
        self._officer_history_dict = dict()
        queryset = OfficerHistory.objects.filter(effective_date__isnull=False)\
            .select_related('unit').values(
                'unit_id', 'officer_id', 'unit__unit_name', 'unit__description',
                'end_date', 'effective_date'
            )
        for officer_history in queryset:
            history_list = self._officer_history_dict.setdefault(
                officer_history['officer_id'],
                SortedKeyList(key=self.history_sort_key))
            history_list.add(officer_history)

    @timing_validate('CRNewTimelineEventIndexer: Populating rank dict...')
    def _populate_rank_dict(self):
        if hasattr(self, '_rank_dict'):
            return
        self._rank_dict = dict()
        for rank in Salary.objects.filter(spp_date__isnull=False).values('officer_id', 'spp_date', 'rank'):
            rank_list = self._rank_dict.setdefault(
                rank['officer_id'],
                SortedKeyList(key=self.rank_sort_key))
            rank_list.add(rank)

    @timing_validate('CRNewTimelineEventIndexer: Populating allegation dict...')
    def _populate_allegation_dict(self):
        if hasattr(self, '_allegation_dict'):
            return
        allegations = Allegation.objects.all()\
            .annotate(coaccused_count=models.Count('officerallegation'))\
            .values('id', 'coaccused_count', 'point', 'crid')
        self._allegation_dict = {
            obj['id']: obj
            for obj in allegations
        }

    @timing_validate('CRNewTimelineEventIndexer: Populating victims dict...')
    def _populate_victims_dict(self):
        if hasattr(self, '_victims_dict'):
            return
        self._victims_dict = dict()
        victims = Victim.objects.all().values('race', 'gender', 'age', 'allegation_id')
        for victim in victims:
            self._victims_dict.setdefault(victim['allegation_id'], []).append(victim)

    @timing_validate('CRNewTimelineEventIndexer: Populating attachments dict...')
    def _populate_attachments_dict(self):
        if hasattr(self, '_attachments_dict'):
            return
        self._attachments_dict = dict()
        attachments = AttachmentFile.objects.all().values(
            'title', 'url', 'preview_image_url', 'file_type', 'allegation_id'
        )
        for obj in attachments:
            self._attachments_dict.setdefault(obj['allegation_id'], []).append(obj)

    def get_queryset(self):
        self._populate_officer_history_dict()
        self._populate_allegation_dict()
        self._populate_attachments_dict()
        self._populate_rank_dict()
        self._populate_victims_dict()
        return OfficerAllegation.objects.filter(start_date__isnull=False)\
            .select_related('allegation_category').values(
            'officer_id', 'allegation_id', 'start_date', 'allegation_category__category',
            'allegation_category__allegation_name', 'final_finding', 'final_outcome'
        )

    def extract_datum(self, datum):
        officer_id = datum['officer_id']
        if officer_id in self._rank_dict:
            rank_list = self._rank_dict[officer_id]
            ind = rank_list.bisect_key_right(datum['start_date'])
            if ind > 0:
                datum['rank'] = rank_list[ind-1]['rank']

        if officer_id in self._officer_history_dict:
            history_list = self._officer_history_dict[officer_id]
            ind = history_list.bisect_key_right(datum['start_date'])
            if ind > 0:
                history = history_list[ind-1]
                if history['end_date'] is None or history['end_date'] >= datum['start_date']:
                    datum['unit_name'] = history['unit__unit_name']
                    datum['unit_description'] = history['unit__description']

        allegation_id = datum['allegation_id']
        allegation = self._allegation_dict[allegation_id]
        datum['crid'] = allegation['crid']
        datum['coaccused_count'] = allegation['coaccused_count']
        datum['point'] = allegation['point']
        datum['victims'] = self._victims_dict.get(allegation_id, [])
        datum['attachments'] = self._attachments_dict.get(allegation_id, [])

        return self.serializer.serialize(datum)


class CRNewTimelineEventPartialIndexer(PartialIndexer, CRNewTimelineEventIndexer):
    def get_batch_queryset(self, keys):
        self._populate_officer_history_dict()
        self._populate_allegation_dict()
        self._populate_attachments_dict()
        self._populate_rank_dict()
        self._populate_victims_dict()
        return OfficerAllegation.objects\
            .filter(start_date__isnull=False, allegation__crid__in=keys)\
            .select_related('allegation_category').values(
                'officer_id', 'allegation_id', 'start_date', 'allegation_category__category',
                'allegation_category__allegation_name', 'final_finding', 'final_outcome'
            )

    def get_postgres_count(self, keys):
        return self.get_batch_queryset(keys).count()

    def get_batch_update_docs_queries(self, keys):
        return self.doc_type_klass.search().query('terms', crid=keys).filter('term', kind='CR')
