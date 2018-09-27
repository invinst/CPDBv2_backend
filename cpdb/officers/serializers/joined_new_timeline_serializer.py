from es_index.serializers import BaseSerializer, get, get_date, literal


class JoinedNewTimelineSerializer(BaseSerializer):
    def __init__(self, *args, **kwargs):
        super(JoinedNewTimelineSerializer, self).__init__(*args, **kwargs)
        self._fields = {
            'officer_id': get('id'),
            'date_sort': get('appointed_date'),
            'priority_sort': literal(10),
            'date': get_date('appointed_date'),
            'kind': literal('JOINED'),
            'unit_name': get('unit_name'),
            'unit_description': get('unit_description'),
            'rank': get('rank')
        }
