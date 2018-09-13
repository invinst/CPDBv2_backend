from django.conf import settings
from django.utils.text import slugify

from rest_framework import serializers

from es_index.serializers import BaseSerializer, get, get_gender, get_date
from data.constants import ACTIVE_CHOICES, ACTIVE_UNKNOWN_CHOICE, MAJOR_AWARDS


class UnitSerializer(BaseSerializer):
    def get_long_unit_name(self, obj):
        return 'Unit %s' % obj['unit__unit_name'] if obj['unit__unit_name'] else 'Unit'

    def __init__(self, *args, **kwargs):
        super(UnitSerializer, self).__init__(*args, **kwargs)
        self._fields = {
            'id': get('unit_id'),
            'unit_name': get('unit__unit_name'),
            'description': get('unit__description'),
            'long_unit_name': self.get_long_unit_name
        }


class OfficerSerializer(BaseSerializer):
    _unit_serializer = UnitSerializer()

    def get_full_name(self, obj):
        return ' '.join([obj['first_name'], obj['last_name']])

    def get_unit(self, obj):
        histories = [
            history for history in obj['history']
            if history['end_date'] is not None
        ]
        if len(histories) == 0:
            return None
        last_history = max(histories, key=lambda o: o['end_date'])
        return self._unit_serializer.serialize(last_history)

    def get_current_badge(self, obj):
        badge_numbers = obj['badgenumber']
        current_badge = [badge for badge in badge_numbers if badge['current']]
        if len(current_badge) == 1:
            return current_badge[0]['star']
        return ''

    def get_historic_badges(self, obj):
        badge_numbers = obj['badgenumber']
        return [badge['star'] for badge in badge_numbers if not badge['current']]

    def get_historic_units(self, obj):
        return [
            self._unit_serializer.serialize(unit)
            for unit in sorted(obj['history'], key=lambda x: x['effective_date'], reverse=True)
        ]

    def get_active(self, obj):
        return dict(ACTIVE_CHOICES).get(obj['active'], ACTIVE_UNKNOWN_CHOICE)

    def _count_for_facet_year(self, entries_dict, facet_value, year, sustained_count_step):
        if facet_value in entries_dict:
            entries_dict[facet_value]['count'] += 1
            entries_dict[facet_value]['sustained_count'] += sustained_count_step
            if year in entries_dict[facet_value]['items']:
                entries_dict[facet_value]['items'][year]['count'] += 1
                entries_dict[facet_value]['items'][year]['sustained_count'] += sustained_count_step
            else:
                entries_dict[facet_value]['items'][year] = {
                    'count': 1,
                    'sustained_count': sustained_count_step
                }
        else:
            entries_dict[facet_value] = {
                'count': 1,
                'sustained_count': sustained_count_step,
                'items': {
                    year: {
                        'count': 1,
                        'sustained_count': sustained_count_step,
                    }
                }
            }

    def get_complainant_aggregation(self, obj, facet_name, facet):
        entries_dict = dict()

        for allegation in obj['allegations']:
            for complaint in allegation['complaints']:
                if complaint['officer_id'] != obj['id']:
                    continue

                if complaint['start_date'] is not None:
                    year = complaint['start_date'].year
                else:
                    year = None
                sustained_count_step = 1 if complaint['final_finding'] == 'SU' else 0
                if len(allegation['complainants']) == 0:
                    self._count_for_facet_year(entries_dict, 'Unknown', year, sustained_count_step)
                    continue

                for complainant in allegation['complainants']:
                    facet_value = complainant[facet]
                    self._count_for_facet_year(entries_dict, facet_value, year, sustained_count_step)

        return {
            'name': facet_name,
            'entries': [
                {
                    'name': k,
                    'count': v['count'],
                    'sustained_count': v['sustained_count'],
                    'items': [
                        {
                            'name': k,
                            'year': ki,
                            'count': vi['count'],
                            'sustained_count': vi['sustained_count']
                        } for ki, vi in v['items'].items()
                    ]
                } for k, v in entries_dict.items()
            ]
        }

    def complaint_items(self, obj):
        items_dict = dict()
        for allegation in obj['allegations']:
            for incident in allegation['complaints']:
                if incident['start_date'] is None or incident['officer_id'] != obj['id']:
                    continue
                year = incident['start_date'].year
                sustained_count_step = 1 if incident['final_finding'] == 'SU' else 0
                if year in items_dict:
                    items_dict[year]['count'] += 1
                    items_dict[year]['sustained_count'] += sustained_count_step
                else:
                    items_dict[year] = {
                        'count': 1,
                        'sustained_count': sustained_count_step
                    }
        return items_dict

    def get_allegation_category_aggregation(self, obj):
        entries_dict = dict()
        for allegation in obj['allegations']:
            for complaint in allegation['complaints']:
                if complaint['officer_id'] != obj['id']:
                    continue

                if complaint['start_date'] is not None:
                    year = complaint['start_date'].year
                else:
                    year = None
                sustained_count_step = 1 if complaint['final_finding'] == 'SU' else 0
                category = complaint['allegation_category__category']
                if category is None:
                    category = 'Unknown'

                if category in entries_dict:
                    entries_dict[category]['count'] += 1
                    entries_dict[category]['sustained_count'] += sustained_count_step
                    if year in entries_dict[category]['items']:
                        entries_dict[category]['items'][year]['count'] += 1
                        entries_dict[category]['items'][year]['sustained_count'] += sustained_count_step
                    else:
                        entries_dict[category]['items'][year] = {
                            'count': 1,
                            'sustained_count': sustained_count_step
                        }
                else:
                    entries_dict[category] = {
                        'count': 1,
                        'sustained_count': sustained_count_step,
                        'items': {
                            year: {
                                'count': 1,
                                'sustained_count': sustained_count_step,
                            }
                        }
                    }

        return {
            'name': 'category',
            'entries': [
                {
                    'name': k,
                    'count': v['count'],
                    'sustained_count': v['sustained_count'],
                    'items': [
                        {
                            'name': k,
                            'year': ki,
                            'count': vi['count'],
                            'sustained_count': vi['sustained_count']
                        } for ki, vi in v['items'].items()
                    ]
                } for k, v in entries_dict.items()
            ]
        }

    def get_complaint_records(self, obj):
        return {
            'count': obj['complaint_count'],
            'sustained_count': obj['sustained_complaint_count'],
            'facets': [
                self.get_allegation_category_aggregation(obj),
                self.get_complainant_aggregation(obj, 'complainant race', 'race'),
                self.get_complainant_aggregation(obj, 'complainant age', 'age'),
                self.get_complainant_aggregation(obj, 'complainant gender', 'gender')
            ],
            'items': [
                {
                    'year': k,
                    'count': v['count'],
                    'sustained_count': v['sustained_count']
                } for k, v in self.complaint_items(obj).items()
            ]
        }

    def get_honorable_mention_count(self, obj):
        count = 0
        for award in obj['awards']:
            if 'Honorable Mention' in award['award_type']:
                count += 1
        return count

    def get_civilian_compliment_count(self, obj):
        count = 0
        for award in obj['awards']:
            if award['award_type'] == 'Complimentary Letter':
                count += 1
        return count

    def get_major_award_count(self, obj):
        count = 0
        for award in obj['awards']:
            if award['award_type'].lower() in MAJOR_AWARDS:
                count += 1
        return count

    def get_has_visual_token(self, obj):
        return all([
            percentile is not None for percentile in [
                obj['civilian_allegation_percentile'],
                obj['internal_allegation_percentile'],
                obj['trr_percentile']
            ]
        ])

    def get_url(self, obj):
        return '{domain}/officer/{slug}/{pk}'.format(
            domain=settings.V1_URL, slug=slugify(self.get_full_name(obj)), pk=obj['id']
        )

    def get_to(self, obj):
        return '/officer/%d/%s/' % (obj['id'], slugify(self.get_full_name(obj)))

    def get_current_salary(self, obj):
        try:
            current_salary_obj = max(obj['salaries'], key=lambda x: x['year'])
            return current_salary_obj['salary']
        except ValueError:
            return None

    def get_coaccusals(self, obj):
        return [
            {'id': key, 'coaccusal_count': val}
            for key, val in obj['coaccusals'].items()
        ]

    def get_current_allegation_percentile(self, obj):
        try:
            lastest_percentiles = max(obj['percentiles'], key=lambda x: x['year'])
            return lastest_percentiles['percentile_allegation']
        except ValueError:
            return None

    def __init__(self, *args, **kwargs):
        super(OfficerSerializer, self).__init__(*args, **kwargs)
        self._fields = {
            'id': get('id'),
            'full_name': self.get_full_name,
            'unit': self.get_unit,
            'rank': get('rank'),
            'race': get('race'),
            'badge': self.get_current_badge,
            'historic_badges': self.get_historic_badges,
            'historic_units': self.get_historic_units,
            'gender': get_gender('gender'),
            'date_of_appt': get_date('appointed_date'),
            'date_of_resignation': get_date('resignation_date'),
            'active': self.get_active,
            'birth_year': get('birth_year'),
            'complaint_records': self.get_complaint_records,
            'allegation_count': get('complaint_count'),
            'complaint_percentile': get('complaint_percentile'),
            'honorable_mention_percentile': get('honorable_mention_percentile'),
            'honorable_mention_count': self.get_honorable_mention_count,
            'has_visual_token': self.get_has_visual_token,
            'sustained_count': get('sustained_complaint_count'),
            'discipline_count': get('discipline_complaint_count'),
            'civilian_compliment_count': self.get_civilian_compliment_count,
            'trr_count': get('trr_count'),
            'major_award_count': self.get_major_award_count,
            'tags': get('tags'),
            'to': self.get_to,
            'url': self.get_url,
            'current_salary': self.get_current_salary,
            'unsustained_count': get('unsustained_complaint_count'),
            'coaccusals': self.get_coaccusals,
            'current_allegation_percentile': self.get_current_allegation_percentile,
            'percentiles': get('percentiles')
        }


class OfficerCoaccusalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    allegation_count = serializers.IntegerField()
    sustained_count = serializers.IntegerField()
    race = serializers.CharField()
    gender = serializers.CharField(source='gender_display')
    birth_year = serializers.IntegerField()
    coaccusal_count = serializers.IntegerField()
    rank = serializers.CharField()

    complaint_percentile = serializers.FloatField(allow_null=True, read_only=True)
    percentile_allegation_civilian = serializers.FloatField(
        allow_null=True, read_only=True, source='civilian_allegation_percentile')
    percentile_allegation_internal = serializers.FloatField(
        allow_null=True, read_only=True, source='internal_allegation_percentile')
    percentile_trr = serializers.FloatField(
        allow_null=True, read_only=True, source='trr_percentile')


class OfficerCoaccusalsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    coaccusals = OfficerCoaccusalSerializer(many=True)
