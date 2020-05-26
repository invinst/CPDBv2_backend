from es_index.serializers import BaseSerializer, get, get_gender


class OfficerCoaccusalSerializer(BaseSerializer):
    def get_full_name(self, obj):
        return f"{obj['first_name']} {obj['last_name']}"

    def get_float(self, field):
        def func(obj):
            return float(obj[field]) if obj[field] is not None else None
        return func

    def __init__(self, *args, **kwargs):
        super(OfficerCoaccusalSerializer, self).__init__(*args, **kwargs)
        self._fields = {
            'id': get('id'),
            'full_name': self.get_full_name,
            'allegation_count': get('complaint_count'),
            'sustained_count': get('sustained_complaint_count'),
            'race': get('race'),
            'gender': get_gender('gender'),
            'birth_year': get('birth_year'),
            'rank': get('rank'),
            'percentile_allegation': self.get_float('complaint_percentile'),
            'percentile_allegation_civilian': self.get_float('civilian_allegation_percentile'),
            'percentile_allegation_internal': self.get_float('internal_allegation_percentile'),
            'percentile_trr': self.get_float('trr_percentile')
        }
