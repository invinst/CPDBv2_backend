from django.db import models

from data.models import (
    OfficerAllegation, AttachmentFile, Victim, Allegation
)
from es_index import register_indexer
from es_index.indexers import BaseIndexer, PartialIndexer
from es_index.utils import timing_validate
from officers.doc_types import OfficerNewTimelineEventDocType
from officers.index_aliases import officers_index_alias
from officers.serializers.cr_new_timeline_serializer import CRNewTimelineSerializer
from officers.query_helpers.officer_unit_by_date import initialize_unit_by_date_helper, get_officer_unit_by_date
from officers.query_helpers.officer_rank_by_date import initialize_rank_by_date_helper, get_officer_rank_by_date

app_name = __name__.split('.')[0]


@register_indexer(app_name)
class CRNewTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerNewTimelineEventDocType
    index_alias = officers_index_alias
    serializer = CRNewTimelineSerializer()

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
        initialize_unit_by_date_helper()
        initialize_rank_by_date_helper()
        self._populate_allegation_dict()
        self._populate_attachments_dict()
        self._populate_victims_dict()
        return OfficerAllegation.objects.filter(start_date__isnull=False)\
            .select_related('allegation_category')

    def extract_datum(self, obj):
        datum = obj.__dict__
        datum['allegation_category__category'] = obj.allegation_category.category
        datum['allegation_category__allegation_name'] = obj.allegation_category.allegation_name
        officer_id = datum['officer_id']
        datum['rank'] = get_officer_rank_by_date(officer_id, datum['start_date'])
        datum['unit_name'], datum['unit_description'] = get_officer_unit_by_date(officer_id, datum['start_date'])

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
        initialize_unit_by_date_helper()
        initialize_rank_by_date_helper()
        self._populate_allegation_dict()
        self._populate_attachments_dict()
        self._populate_victims_dict()
        return OfficerAllegation.objects\
            .filter(start_date__isnull=False, allegation__crid__in=keys)\
            .select_related('allegation_category')

    def get_batch_update_docs_queries(self, keys):
        return self.doc_type_klass.search().query('terms', crid=keys).filter('term', kind='CR')
