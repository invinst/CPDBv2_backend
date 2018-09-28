from es_index.serializers import BaseSerializer, get, literal, get_date


class UnitChangeNewTimelineSerializer(BaseSerializer):
    def __init__(self, *args, **kwargs):
        super(UnitChangeNewTimelineSerializer, self).__init__(*args, **kwargs)
        self._fields = {
            'officer_id': get('officer_id'),
            'date_sort': get('effective_date'),
            'priority_sort': literal(20),
            'date': get_date('effective_date'),
            'kind': literal('UNIT_CHANGE'),
            'unit_name': get('unit_name'),
            'unit_description': get('unit_description'),
            'rank': get('rank')
        }
