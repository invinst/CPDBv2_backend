from rest_framework import serializers

from data.models import PoliceUnit


class PoliceUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliceUnit
        fields = ['id', 'unit_name', 'description']


class OfficerSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    unit = PoliceUnitSerializer(source='last_unit')
    date_of_appt = serializers.DateField(source='appointed_date', format='%Y-%m-%d')
    date_of_resignation = serializers.DateField(source='resignation_date', format='%Y-%m-%d')
    active = serializers.SerializerMethodField()
    rank = serializers.CharField()
    full_name = serializers.CharField()
    race = serializers.CharField()
    badge = serializers.CharField(source='current_badge')
    historic_badges = serializers.ListField(child=serializers.CharField())
    historic_units = PoliceUnitSerializer(many=True, read_only=True)
    gender = serializers.CharField(source='gender_display')
    complaint_records = serializers.SerializerMethodField()
    birth_year = serializers.IntegerField()
    current_salary = serializers.IntegerField()

    def get_complaint_records(self, obj):
        return {
            'count': obj.allegation_count,
            'sustained_count': obj.sustained_count,
            'facets': [
                {'name': 'category', 'entries': obj.complaint_category_aggregation},
                {'name': 'complainant race', 'entries': obj.complainant_race_aggregation},
                {'name': 'complainant age', 'entries': obj.complainant_age_aggregation},
                {'name': 'complainant gender', 'entries': obj.complainant_gender_aggregation},
            ],
            'items': obj.total_complaints_aggregation
        }

    def get_active(self, obj):
        return obj.get_active_display()


class OfficerSinglePercentileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    honorable_mention_percentile = serializers.FloatField(source='percentile_honorable_mention')


class OfficerMetricsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    allegation_count = serializers.IntegerField()
    complaint_percentile = serializers.FloatField()
    honorable_mention_count = serializers.IntegerField()
    sustained_count = serializers.IntegerField()
    unsustained_count = serializers.IntegerField()
    discipline_count = serializers.IntegerField()
    civilian_compliment_count = serializers.IntegerField()
    trr_count = serializers.IntegerField()
    major_award_count = serializers.IntegerField()
    single_percentiles = OfficerSinglePercentileSerializer(read_only=True)


class OfficerYearlyPercentileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    year = serializers.IntegerField()
    percentile_trr = serializers.DecimalField(
        allow_null=True, read_only=True, max_digits=6, decimal_places=3)
    percentile_allegation = serializers.DecimalField(
        allow_null=True, read_only=True, max_digits=6, decimal_places=3)
    percentile_allegation_civilian = serializers.DecimalField(
        allow_null=True, read_only=True, max_digits=6, decimal_places=3)
    percentile_allegation_internal = serializers.DecimalField(
        allow_null=True, read_only=True, max_digits=6, decimal_places=3)


class CoaccusalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    coaccusal_count = serializers.IntegerField()


class OfficerInfoSerializer(OfficerSummarySerializer, OfficerMetricsSerializer):
    percentiles = OfficerYearlyPercentileSerializer(many=True, read_only=True)
    to = serializers.CharField(source='v2_to')
    url = serializers.CharField(source='v1_url')
    tags = serializers.ListField(child=serializers.CharField())
    coaccusals = CoaccusalSerializer(many=True, read_only=True)


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
    complaint_percentile = serializers.FloatField()
    race = serializers.CharField()
    gender = serializers.CharField(source='gender_display')
    birth_year = serializers.IntegerField()
    coaccusal_count = serializers.IntegerField()
    rank = serializers.CharField()


class OfficerCoaccusalsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    coaccusals = OfficerCoaccusalSerializer(many=True)
