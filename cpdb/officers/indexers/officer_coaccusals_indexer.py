import itertools

from django.db import models

from data.models import Officer, OfficerAllegation
from data.utils.subqueries import SQCount
from es_index import register_indexer
from es_index.utils import timing_validate
from es_index.indexers import BaseIndexer
from officers.doc_types import (
    OfficerCoaccusalsDocType,
)
from officers.index_aliases import officers_index_alias
from officers.serializers.officer_coaccusals_serializer import OfficerCoaccusalSerializer

app_name = __name__.split('.')[0]


@register_indexer(app_name)
class OfficerCoaccusalsIndexer(BaseIndexer):
    doc_type_klass = OfficerCoaccusalsDocType
    index_alias = officers_index_alias
    serializer = OfficerCoaccusalSerializer()

    @timing_validate('OfficerCoaccusalsIndexer: Populating coaccusal dict...')
    def _populate_coaccusal_dict(self):
        self._coaccusal_dict = dict()
        allegation_dict = dict()
        for obj in OfficerAllegation.objects.all():
            allegation_dict.setdefault(obj.allegation_id, []).append(obj.officer_id)

        for officer_ids in allegation_dict.values():
            if len(officer_ids) < 2:
                continue
            for id_1, id_2 in itertools.permutations(officer_ids, 2):
                d1 = self._coaccusal_dict.setdefault(id_1, dict())
                d1[id_2] = d1.get(id_2, 0) + 1

    @timing_validate('OfficerCoaccusalsIndexer: Populating officers dict...')
    def _populate_officers_dict(self):
        self._officer_dict = dict()
        allegation_count = OfficerAllegation.objects.filter(
            officer=models.OuterRef('id')
        )
        sustained_count = OfficerAllegation.objects.filter(
            officer=models.OuterRef('id'),
            final_finding='SU'
        )
        queryset = Officer.objects.all()\
            .annotate(complaint_count=SQCount(allegation_count.values('id')))\
            .annotate(sustained_complaint_count=SQCount(sustained_count.values('id')))
        for officer in queryset:
            self._officer_dict[officer.id] = self.serializer.serialize(officer.__dict__)

    def get_queryset(self):
        self._populate_coaccusal_dict()
        self._populate_officers_dict()
        return Officer.objects.all()

    def extract_datum(self, officer):
        return {
            'id': officer.id,
            'coaccusals': [
                dict(
                    [('coaccusal_count', count)] +
                    self._officer_dict[coaccused_id].items()
                )
                for coaccused_id, count in
                sorted(
                    self._coaccusal_dict.get(officer.id, dict()).items(),
                    key=lambda t: t[0]
                )
            ]
        }
