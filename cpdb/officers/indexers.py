from es_index import register_indexer
from es_index.indexers import BaseIndexer
from data.models import Officer, OfficerAllegation, OfficerHistory
from .doc_types import OfficerSummaryDocType, OfficerTimelineEventDocType
from .serializers import OfficerSummarySerializer, CRTimelineSerializer, UnitChangeTimelineSerializer


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
