from es_index.serializers import BaseSerializer, get, literal, get_date, get_point


class TRRNewTimelineSerializer(BaseSerializer):
    def get_date_sort(self, obj):
        try:
            return obj['trr_datetime'].date()
        except AttributeError:
            return None

    def __init__(self, *args, **kwargs):
        super(TRRNewTimelineSerializer, self).__init__(*args, **kwargs)
        self._fields = {
            'trr_id': get('id'),
            'officer_id': get('officer_id'),
            'date_sort': self.get_date_sort,
            'priority_sort': literal(50),
            'date': get_date('trr_datetime'),
            'kind': literal('FORCE'),
            'taser': get('taser'),
            'firearm_used': get('firearm_used'),
            'unit_name': get('unit_name'),
            'unit_description': get('unit_description'),
            'rank': get('rank'),
            'point': get_point('point')
        }
