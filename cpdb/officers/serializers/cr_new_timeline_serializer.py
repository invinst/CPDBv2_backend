from es_index.serializers import (
    BaseSerializer, get_gender, get, get_date, literal, get_finding, get_point
)


class _VictimSerializer(BaseSerializer):
    def __init__(self, *args, **kwargs):
        super(_VictimSerializer, self).__init__(*args, **kwargs)
        self._fields = {
            'race': get('race'),
            'gender': get_gender('gender'),
            'age': get('age')
        }


class _AttachmentSerializer(BaseSerializer):
    def __init__(self, *args, **kwargs):
        super(_AttachmentSerializer, self).__init__(*args, **kwargs)
        self._fields = {
            'title': get('title'),
            'url': get('url'),
            'preview_image_url': get('preview_image_url'),
            'file_type': get('file_type')
        }


class CRNewTimelineSerializer(BaseSerializer):
    def __init__(self, *args, **kwargs):
        super(CRNewTimelineSerializer, self).__init__(*args, **kwargs)
        self._fields = {
            'officer_id': get('officer_id'),
            'date_sort': get('start_date'),
            'priority_sort': literal(30),
            'date': get_date('start_date'),
            'kind': literal('CR'),
            'crid': get('crid'),
            'category': get('allegation_category__category'),
            'subcategory': get('allegation_category__allegation_name'),
            'finding': get_finding('final_finding'),
            'outcome': get('final_outcome'),
            'coaccused': get('coaccused_count'),
            'unit_name': get('unit_name'),
            'unit_description': get('unit_description'),
            'rank': get('rank'),
            'victims': _VictimSerializer('victims'),
            'attachments': _AttachmentSerializer('attachments'),
            'point': get_point('point')
        }
