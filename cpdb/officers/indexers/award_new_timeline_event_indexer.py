from es_index import register_indexer
from es_index.indexers import BaseIndexer
from data.models import Award
from officers.doc_types import OfficerNewTimelineEventDocType
from officers.index_aliases import officers_index_alias
from officers.query_helpers.officer_rank_by_date import initialize_rank_by_date_helper, get_officer_rank_by_date
from officers.query_helpers.officer_unit_by_date import initialize_unit_by_date_helper, get_officer_unit_by_date
from officers.serializers.award_new_timeline_event_serializer import AwardNewTimelineSerializer

app_name = __name__.split('.')[0]


@register_indexer(app_name)
class AwardNewTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerNewTimelineEventDocType
    index_alias = officers_index_alias
    serializer = AwardNewTimelineSerializer()

    def get_queryset(self):
        initialize_rank_by_date_helper()
        initialize_unit_by_date_helper()
        return Award.objects.filter(start_date__isnull=False)\
            .exclude(award_type__contains='Honorable Mention')\
            .exclude(award_type__in=['Complimentary Letter', 'Department Commendation'])

    def extract_datum(self, obj):
        datum = obj.__dict__
        unit_name, unit_description = get_officer_unit_by_date(obj.officer_id, datum['start_date'])
        datum['unit_name'] = unit_name if unit_name is not None else ''
        datum['unit_description'] = unit_description if unit_description is not None else ''
        datum['rank'] = get_officer_rank_by_date(obj.officer_id, datum['start_date'])
        return self.serializer.serialize(datum)
