from es_index.serializers import BaseSerializer, get, get_date, literal


class RankChangeNewTimelineSerializer(BaseSerializer):
    def __init__(self, *args, **kwargs):
        super(RankChangeNewTimelineSerializer, self).__init__(*args, **kwargs)
        self._fields = {
            'officer_id': get('officer_id'),
            'date_sort': get('spp_date'),
            'priority_sort': literal(25),
            'date': get_date('spp_date'),
            'kind': literal('RANK_CHANGE'),
            'unit_name': get('unit_name', ''),
            'unit_description': get('unit_description', ''),
            'rank': get('rank')
        }
