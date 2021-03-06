from django.utils import timezone

from es_index.serializers import (
    BaseSerializer, get, get_gender, get_date, literal, get_finding, get_point
)


class CoaccusedSerializer(BaseSerializer):
    def get_full_name(self, obj):
        return ' '.join([obj['officer__first_name'], obj['officer__last_name']])

    def get_abbr_name(self, obj):
        return '. '.join([obj['officer__first_name'][0].upper(), obj['officer__last_name']])

    def get_age(self, obj):
        if obj['officer__birth_year'] is not None:
            return timezone.localtime(timezone.now()).year - obj['officer__birth_year']

        return None

    def __init__(self, *args, **kwargs):
        super(CoaccusedSerializer, self).__init__(*args, **kwargs)
        self._fields = {
            'id': get('officer_id'),
            'full_name': self.get_full_name,
            'abbr_name': self.get_abbr_name,
            'gender': get_gender('officer__gender'),
            'race': get('officer__race'),
            'rank': get('officer__rank'),
            'final_outcome': get('final_outcome'),
            'final_finding': get_finding('final_finding', 'Unknown'),
            'recc_outcome': get('recc_outcome'),
            'category': get('allegation_category__category'),
            'subcategory': get('allegation_category__allegation_name'),
            'start_date': get_date('start_date'),
            'end_date': get_date('end_date'),
            'age': self.get_age,
            'allegation_count': get('allegation_count'),
            'sustained_count': get('sustained_count'),
            'disciplined': get('disciplined'),
            'percentile_allegation': get('officer__complaint_percentile'),
            'percentile_allegation_civilian': get('officer__civilian_allegation_percentile'),
            'percentile_allegation_internal': get('officer__internal_allegation_percentile'),
            'percentile_trr': get('officer__trr_percentile')
        }


class InvestigatorSerializer(BaseSerializer):
    def get_full_name(self, obj):
        if obj['investigator__officer__first_name'] is not None:
            return ' '.join(list(filter(None, [
                obj['investigator__officer__first_name'], obj['investigator__officer__last_name']
            ])))
        return ' '.join(list(filter(None, [obj['investigator__first_name'], obj['investigator__last_name']])))

    def get_abbr_name(self, obj):
        if obj['investigator__officer__first_name'] is not None and obj['investigator__officer__last_name'] is not None:
            return '. '.join([
                obj['investigator__officer__first_name'][0].upper(), obj['investigator__officer__last_name']
            ])
        elif obj['investigator__first_name'] is not None and obj['investigator__last_name'] is not None:
            return '. '.join([obj['investigator__first_name'][0].upper(), obj['investigator__last_name']])
        return None

    def __init__(self, *args, **kwargs):
        super(InvestigatorSerializer, self).__init__(*args, **kwargs)
        self._fields = {
            'officer_id': get('investigator__officer_id'),
            'involved_type': literal('investigator'),
            'full_name': self.get_full_name,
            'abbr_name': self.get_abbr_name,
            'percentile_allegation': get('investigator__officer__complaint_percentile'),
            'percentile_allegation_civilian': get('investigator__officer__civilian_allegation_percentile'),
            'percentile_allegation_internal': get('investigator__officer__internal_allegation_percentile'),
            'percentile_trr': get('investigator__officer__trr_percentile'),
            'num_cases': get('num_cases'),
            'current_rank': get('current_rank')
        }


class PoliceWitnessSerializer(BaseSerializer):
    def get_full_name(self, obj):
        return ' '.join([obj['officer__first_name'], obj['officer__last_name']])

    def get_abbr_name(self, obj):
        return '. '.join([obj['officer__first_name'][0].upper(), obj['officer__last_name']])

    def __init__(self, *args, **kwargs):
        super(PoliceWitnessSerializer, self).__init__(*args, **kwargs)
        self._fields = {
            'officer_id': get('officer_id'),
            'involved_type': literal('police_witness'),
            'full_name': self.get_full_name,
            'abbr_name': self.get_abbr_name,
            'allegation_count': get('allegation_count'),
            'sustained_count': get('sustained_count'),
            'gender': get_gender('officer__gender'),
            'race': get('officer__race'),
            'percentile_allegation': get('officer__complaint_percentile'),
            'percentile_allegation_civilian': get('officer__civilian_allegation_percentile'),
            'percentile_allegation_internal': get('officer__internal_allegation_percentile'),
            'percentile_trr': get('officer__trr_percentile')
        }


class DemographicSerializer(BaseSerializer):
    def __init__(self, *args, **kwargs):
        super(DemographicSerializer, self).__init__(*args, **kwargs)
        self._fields = {
            'gender': get_gender('gender'),
            'race': get('race'),
            'age': get('age')
        }


class AttachmentSerializer(BaseSerializer):
    def __init__(self, *args, **kwargs):
        super(AttachmentSerializer, self).__init__(*args, **kwargs)
        self._fields = {
            'title': get('title'),
            'url': get('url'),
            'preview_image_url': get('preview_image_url'),
            'file_type': get('file_type')
        }


class AllegationSerializer(BaseSerializer):
    investigator_serializer = InvestigatorSerializer(key='investigators')
    police_witness_serializer = PoliceWitnessSerializer(key='police_witnesses')

    def get_most_common_category(self, obj):
        category_count = dict()
        for accused in obj['coaccused']:
            category = category_count.setdefault(accused['allegation_category_id'], {
                'allegation_name': accused['allegation_category__allegation_name'],
                'category': accused['allegation_category__category'],
                'count': 0
            })
            category['count'] += 1

        try:
            result = max(category_count.values(), key=lambda obj: obj['count'])
            result.pop('count')
            return result
        except ValueError:
            return None

    def get_any_start_date(self, obj):
        for accused in obj['coaccused']:
            if accused['start_date'] is not None:
                return accused['start_date'].strftime('%Y-%m-%d')
        return None

    def get_any_end_date(self, obj):
        for accused in obj['coaccused']:
            if accused['end_date'] is not None:
                return accused['end_date'].strftime('%Y-%m-%d')
        return None

    def get_address(self, obj):
        if obj['old_complaint_address'] is not None:
            return obj['old_complaint_address']
        result = ' '.join(list(filter(None, [obj['add1'], obj['add2']])))
        return ', '.join(list(filter(None, [result, obj['city']])))

    def get_involvements(self, obj):
        return AllegationSerializer.investigator_serializer(obj) + \
            AllegationSerializer.police_witness_serializer(obj)

    def get_categories(self, obj):
        return list(set([accused['allegation_category__category'] for accused in obj['coaccused']]))

    def __init__(self, *args, **kwargs):
        super(AllegationSerializer, self).__init__(*args, **kwargs)
        self._fields = {
            'crid': get('crid'),
            'most_common_category': self.get_most_common_category,
            'coaccused': CoaccusedSerializer(key='coaccused'),
            'summary': get('summary'),
            'point': get_point('point'),
            'incident_date': get_date('incident_date'),
            'start_date': self.get_any_start_date,
            'end_date': self.get_any_end_date,
            'address': self.get_address,
            'location': get('location'),
            'beat': get('beat__name'),
            'involvements': self.get_involvements,
            'category_names': self.get_categories,
            'complainants': DemographicSerializer(key='complainants'),
            'victims': DemographicSerializer(key='victims'),
            'attachments': AttachmentSerializer(key='attachments')
        }
