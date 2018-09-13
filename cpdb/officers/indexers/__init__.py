from data.models import Officer
from es_index import register_indexer
from es_index.indexers import BaseIndexer
from trr.models import TRR
from officers.doc_types import (
    OfficerNewTimelineEventDocType,
    OfficerCoaccusalsDocType,
)
from officers.index_aliases import officers_index_alias
from officers.serializers.doc_serializers import (
    TRRNewTimelineSerializer,
    OfficerCoaccusalsSerializer
)
from .officers_indexer import OfficersIndexer
from .cr_new_timeline_indexer import CRNewTimelineEventIndexer, CRNewTimelineEventPartialIndexer
from .unit_change_new_timeline_event_indexer import UnitChangeNewTimelineEventIndexer
from .rank_change_new_timeline_event_indexer import RankChangeNewTimelineEventIndexer
from .joined_new_timeline_event_indexer import JoinedNewTimelineEventIndexer
from .award_new_timeline_event_indexer import AwardNewTimelineEventIndexer

app_name = __name__.split('.')[0]


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


__all__ = [
    'OfficersIndexer', 'CRNewTimelineEventIndexer', 'UnitChangeNewTimelineEventIndexer',
    'RankChangeNewTimelineEventIndexer', 'JoinedNewTimelineEventIndexer', 'AwardNewTimelineEventIndexer',
    'TRRNewTimelineEventIndexer', 'OfficerCoaccusalsIndexer', 'CRNewTimelineEventPartialIndexer'
]
