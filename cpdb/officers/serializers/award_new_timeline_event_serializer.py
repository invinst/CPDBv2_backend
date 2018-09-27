from es_index.serializers import BaseSerializer, get, get_date, literal


class AwardNewTimelineSerializer(BaseSerializer):
    def __init__(self, *args, **kwargs):
        super(AwardNewTimelineSerializer, self).__init__(*args, **kwargs)
        self._fields = {
            'officer_id': get('officer_id'),
            'date_sort': get('start_date'),
            'priority_sort': literal(40),
            'date': get_date('start_date'),
            'kind': literal('AWARD'),
            'award_type': get('award_type'),
            'unit_name': get('unit_name'),
            'unit_description': get('unit_description'),
            'rank': get('rank')
        }
