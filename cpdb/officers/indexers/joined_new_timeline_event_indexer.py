from data.models import Officer
from es_index.indexers import BaseIndexer
from es_index import register_indexer
from officers.doc_types import OfficerNewTimelineEventDocType
from officers.index_aliases import officers_index_alias
from officers.serializers.joined_new_timeline_serializer import JoinedNewTimelineSerializer
from officers.query_helpers.officer_rank_by_date import initialize_rank_by_date_helper, get_officer_rank_by_date
from officers.query_helpers.officer_unit_by_date import initialize_unit_by_date_helper, get_officer_unit_by_date

app_name = __name__.split('.')[0]


@register_indexer(app_name)
class JoinedNewTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerNewTimelineEventDocType
    index_alias = officers_index_alias
    serializer = JoinedNewTimelineSerializer()

    def get_queryset(self):
        initialize_rank_by_date_helper()
        initialize_unit_by_date_helper()
        return Officer.objects.filter(appointed_date__isnull=False)

    def extract_datum(self, obj):
        datum = obj.__dict__
        unit_name, unit_description = get_officer_unit_by_date(obj.id, datum['appointed_date'])
        datum['unit_name'] = unit_name if unit_name is not None else ''
        datum['unit_description'] = unit_description if unit_description is not None else ''
        datum['rank'] = get_officer_rank_by_date(obj.id, datum['appointed_date'])
        return self.serializer.serialize(datum)
