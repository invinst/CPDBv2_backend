from django.conf import settings
from django.utils.text import slugify

from rest_framework import serializers

from es_index.serializers import BaseSerializer, get, get_gender, get_date
from data.models import PoliceUnit
from data.constants import ACTIVE_CHOICES, ACTIVE_UNKNOWN_CHOICE, MAJOR_AWARDS


class UnitSerializer(BaseSerializer):
    def get_long_unit_name(self, obj):
        return 'Unit %s' % obj['unit_name'] if obj['unit_name'] else 'Unit'

    def __init__(self, *args, **kwargs):
        super(UnitSerializer, self).__init__(*args, **kwargs)
        self._fields = {
            'id': get('unit_id'),
            'unit_name': get('unit_name'),
            'description': get('description'),
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
                category = complaint['category']
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
            'count': obj['allegation_count'],
            'sustained_count': obj['sustained_count'],
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
        return '/officer/%d/' % obj['id']

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
        if obj['percentile_allegation'] is None:
            return None

        return '%.4f' % obj['percentile_allegation']

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
            'date_of_appt': get_date('date_of_appt'),
            'date_of_resignation': get_date('date_of_resignation'),
            'active': self.get_active,
            'birth_year': get('birth_year'),
            'complaint_records': self.get_complaint_records,
            'allegation_count': get('allegation_count'),
            'complaint_percentile': get('complaint_percentile'),
            'honorable_mention_percentile': get('honorable_mention_percentile'),
            'honorable_mention_count': self.get_honorable_mention_count,
            'has_visual_token': self.get_has_visual_token,
            'sustained_count': get('sustained_count'),
            'discipline_count': get('discipline_count'),
            'civilian_compliment_count': self.get_civilian_compliment_count,
            'trr_count': get('trr_count'),
            'major_award_count': self.get_major_award_count,
            'tags': get('tags'),
            'to': self.get_to,
            'url': self.get_url,
            'current_salary': self.get_current_salary,
            'unsustained_count': get('unsustained_count'),
            'coaccusals': self.get_coaccusals,
            'current_allegation_percentile': self.get_current_allegation_percentile
        }


class OfficerYearlyPercentileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    year = serializers.IntegerField()
    percentile_trr = serializers.DecimalField(
        allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation = serializers.DecimalField(
        allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation_civilian = serializers.DecimalField(
        allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation_internal = serializers.DecimalField(
        allow_null=True, read_only=True, max_digits=6, decimal_places=4)


class CoaccusalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    coaccusal_count = serializers.IntegerField()


class JoinedNewTimelineSerializer(serializers.Serializer):
    officer_id = serializers.IntegerField(source='id')
    date_sort = serializers.DateField(source='appointed_date', format=None)
    priority_sort = serializers.SerializerMethodField()
    date = serializers.DateField(source='appointed_date', format='%Y-%m-%d')
    kind = serializers.SerializerMethodField()
    unit_name = serializers.SerializerMethodField()
    unit_description = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return 'JOINED'

    def get_priority_sort(self, obj):
        return 10

    def get_unit_name(self, obj):
        unit = obj.get_unit_by_date(obj.appointed_date)
        return unit.unit_name if unit else ''

    def get_unit_description(self, obj):
        unit = obj.get_unit_by_date(obj.appointed_date)
        return unit.description if unit else ''

    def get_rank(self, obj):
        return obj.get_rank_by_date(obj.appointed_date)


class UnitChangeNewTimelineSerializer(serializers.Serializer):
    officer_id = serializers.IntegerField()
    date_sort = serializers.DateField(source='effective_date', format=None)
    priority_sort = serializers.SerializerMethodField()
    date = serializers.DateField(source='effective_date', format='%Y-%m-%d')
    kind = serializers.SerializerMethodField()
    unit_name = serializers.CharField()
    unit_description = serializers.CharField()
    rank = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return 'UNIT_CHANGE'

    def get_priority_sort(self, obj):
        return 20

    def get_rank(self, obj):
        return obj.officer.get_rank_by_date(obj.effective_date)


class RankChangeNewTimelineSerializer(serializers.Serializer):
    officer_id = serializers.IntegerField()
    date_sort = serializers.DateField(source='spp_date', format=None)
    priority_sort = serializers.SerializerMethodField()
    date = serializers.DateField(source='spp_date', format='%Y-%m-%d')
    kind = serializers.SerializerMethodField()
    unit_name = serializers.SerializerMethodField()
    unit_description = serializers.SerializerMethodField()
    rank = serializers.CharField()

    def get_kind(self, obj):
        return 'RANK_CHANGE'

    def get_priority_sort(self, obj):
        return 25

    def get_unit_name(self, obj):
        unit = obj.officer.get_unit_by_date(obj.spp_date)
        return unit.unit_name if unit else ''

    def get_unit_description(self, obj):
        unit = obj.officer.get_unit_by_date(obj.spp_date)
        return unit.description if unit else ''


class VictimSerializer(serializers.Serializer):
    gender = serializers.CharField(source='gender_display')
    race = serializers.CharField()
    age = serializers.IntegerField()


class AttachmentFileSerializer(serializers.Serializer):
    title = serializers.CharField()
    url = serializers.CharField()
    preview_image_url = serializers.CharField()
    file_type = serializers.CharField()


class CRNewTimelineSerializer(serializers.Serializer):
    officer_id = serializers.IntegerField()
    date_sort = serializers.DateField(source='start_date', format=None)
    date = serializers.DateField(source='start_date', format='%Y-%m-%d')
    priority_sort = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()
    crid = serializers.CharField()
    category = serializers.SerializerMethodField()
    subcategory = serializers.CharField()
    finding = serializers.CharField(source='final_finding_display')
    outcome = serializers.CharField(source='final_outcome')
    coaccused = serializers.IntegerField(source='coaccused_count')
    unit_name = serializers.SerializerMethodField()
    unit_description = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()
    attachments = AttachmentFileSerializer(many=True)
    point = serializers.SerializerMethodField()
    victims = VictimSerializer(many=True)

    def get_category(self, obj):
        return obj.category if obj.category else 'Unknown'

    def get_kind(self, obj):
        return 'CR'

    def get_priority_sort(self, obj):
        return 30

    def get_unit_name(self, obj):
        unit = obj.officer.get_unit_by_date(obj.start_date)
        return unit.unit_name if unit else ''

    def get_unit_description(self, obj):
        unit = obj.officer.get_unit_by_date(obj.start_date)
        return unit.description if unit else ''

    def get_rank(self, obj):
        return obj.officer.get_rank_by_date(obj.start_date)

    def get_point(self, obj):
        try:
            return {
                'lon': obj.allegation.point.x,
                'lat': obj.allegation.point.y
            }
        except AttributeError:
            return None


class AwardNewTimelineSerializer(serializers.Serializer):
    officer_id = serializers.IntegerField()
    date_sort = serializers.DateField(source='start_date', format=None)
    priority_sort = serializers.SerializerMethodField()
    date = serializers.DateField(source='start_date', format='%Y-%m-%d')
    kind = serializers.SerializerMethodField()
    award_type = serializers.CharField()
    unit_name = serializers.SerializerMethodField()
    unit_description = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return 'AWARD'

    def get_priority_sort(self, obj):
        return 40

    def get_unit_name(self, obj):
        unit = obj.officer.get_unit_by_date(obj.start_date)
        return unit.unit_name if unit else ''

    def get_unit_description(self, obj):
        unit = obj.officer.get_unit_by_date(obj.start_date)
        return unit.description if unit else ''

    def get_rank(self, obj):
        return obj.officer.get_rank_by_date(obj.start_date)


class TRRNewTimelineSerializer(serializers.Serializer):
    trr_id = serializers.IntegerField(source='id')
    officer_id = serializers.IntegerField()
    date_sort = serializers.SerializerMethodField()
    priority_sort = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()
    taser = serializers.NullBooleanField()
    firearm_used = serializers.NullBooleanField()
    unit_name = serializers.SerializerMethodField()
    unit_description = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return 'FORCE'

    def get_priority_sort(self, obj):
        return 50

    def get_unit_name(self, obj):
        unit = obj.officer.get_unit_by_date(obj.trr_datetime)
        return unit.unit_name if unit else ''

    def get_unit_description(self, obj):
        unit = obj.officer.get_unit_by_date(obj.trr_datetime)
        return unit.description if unit else ''

    def get_rank(self, obj):
        return obj.officer.get_rank_by_date(obj.trr_datetime.date())

    def get_date_sort(self, obj):
        return obj.trr_datetime.date()

    def get_date(self, obj):
        return obj.trr_datetime.date().strftime(format='%Y-%m-%d')

    def get_point(self, obj):
        try:
            return {
                'lon': obj.point.x,
                'lat': obj.point.y
            }
        except AttributeError:
            return None


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
