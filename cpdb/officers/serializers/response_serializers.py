from rest_framework import serializers

from data.constants import MAX_VISUAL_TOKEN_YEAR
from data.models import PoliceUnit
from shared.serializer import NoNullSerializer


class OfficerPercentileSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    year = serializers.SerializerMethodField()
    percentile_trr = serializers.DecimalField(
        source='trr_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation = serializers.DecimalField(
        source='complaint_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation_civilian = serializers.DecimalField(
        source='civilian_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation_internal = serializers.DecimalField(
        source='internal_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)

    def get_year(self, obj):
        return min(obj.resignation_date.year, MAX_VISUAL_TOKEN_YEAR) if obj.resignation_date else MAX_VISUAL_TOKEN_YEAR


class OfficerCardSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    complaint_count = serializers.IntegerField(source='allegation_count')
    sustained_count = serializers.IntegerField()
    birth_year = serializers.IntegerField()
    complaint_percentile = serializers.FloatField(read_only=True, allow_null=True)
    race = serializers.CharField()
    gender = serializers.CharField(source='gender_display')
    rank = serializers.CharField()
    percentile = serializers.SerializerMethodField()

    def get_percentile(self, obj):
        return OfficerPercentileSerializer(obj).data


class PoliceUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliceUnit
        fields = ['id', 'unit_name', 'description', 'long_unit_name']

    long_unit_name = serializers.SerializerMethodField()

    def get_long_unit_name(self, obj):
        return f'Unit {obj.unit_name}' if obj.unit_name else 'Unit'


class OfficerSummarySerializer(NoNullSerializer):
    id = serializers.IntegerField()
    unit = PoliceUnitSerializer(source='last_unit')
    date_of_appt = serializers.DateField(source='appointed_date', format='%Y-%m-%d')
    date_of_resignation = serializers.DateField(source='resignation_date', format='%Y-%m-%d')
    active = serializers.SerializerMethodField()
    rank = serializers.CharField()
    full_name = serializers.CharField()
    has_unique_name = serializers.BooleanField()
    race = serializers.CharField()
    badge = serializers.SerializerMethodField()
    historic_badges = serializers.ListField(child=serializers.CharField())
    historic_units = PoliceUnitSerializer(many=True, read_only=True)
    gender = serializers.CharField(source='gender_display')
    birth_year = serializers.IntegerField()
    current_salary = serializers.IntegerField()

    def get_active(self, obj):
        return obj.get_active_display()

    def get_badge(self, obj):
        return obj.current_badge or ''


class OfficerMetricsSerializer(NoNullSerializer):
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
    honorable_mention_percentile = serializers.FloatField(allow_null=True, read_only=True)


class OfficerYearlyPercentileSerializer(NoNullSerializer):
    id = serializers.IntegerField(source='officer_id')
    year = serializers.IntegerField()
    percentile_trr = serializers.DecimalField(
        allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation = serializers.DecimalField(
        allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation_civilian = serializers.DecimalField(
        allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation_internal = serializers.DecimalField(
        allow_null=True, read_only=True, max_digits=6, decimal_places=4)


class CoaccusalSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    coaccusal_count = serializers.IntegerField()


class OfficerInfoSerializer(OfficerSummarySerializer, OfficerMetricsSerializer):
    percentiles = serializers.SerializerMethodField()
    to = serializers.CharField(source='v2_to')
    url = serializers.CharField(source='v1_url')
    tags = serializers.ListField(child=serializers.CharField())
    coaccusals = CoaccusalSerializer(many=True, read_only=True)

    def get_percentiles(self, obj):
        yearly_percentiles = obj.officeryearlypercentile_set.order_by('year')
        return OfficerYearlyPercentileSerializer(yearly_percentiles, many=True).data


class BaseTimelineSerializer(NoNullSerializer):
    unit_name = serializers.SerializerMethodField()
    unit_description = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()
    priority_sort = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()

    def get_kind(self, obj):
        raise NotImplementedError

    def get_priority_sort(self, obj):
        raise NotImplementedError

    def get_unit_name(self, obj):
        return obj.unit_name if obj.unit_name else ''

    def get_unit_description(self, obj):
        return obj.unit_description if obj.unit_description else ''

    def get_rank(self, obj):
        return obj.rank_name


class RankChangeNewTimelineSerializer(BaseTimelineSerializer):
    date_sort = serializers.DateField(source='spp_date', format=None)
    date = serializers.DateField(source='spp_date', format='%Y-%m-%d')

    def get_kind(self, obj):
        return 'RANK_CHANGE'

    def get_priority_sort(self, obj):
        return 25

    def get_rank(self, obj):
        return obj.rank


class JoinedNewTimelineSerializer(BaseTimelineSerializer):
    date_sort = serializers.DateField(source='appointed_date', format=None)
    date = serializers.DateField(source='appointed_date', format='%Y-%m-%d')

    def get_kind(self, obj):
        return 'JOINED'

    def get_priority_sort(self, obj):
        return 10


class UnitChangeNewTimelineSerializer(BaseTimelineSerializer):
    date_sort = serializers.DateField(source='effective_date', format=None)
    date = serializers.DateField(source='effective_date', format='%Y-%m-%d')

    def get_kind(self, obj):
        return 'UNIT_CHANGE'

    def get_priority_sort(self, obj):
        return 20


class VictimSerializer(NoNullSerializer):
    gender = serializers.CharField(source='gender_display')
    race = serializers.CharField()
    age = serializers.IntegerField()


class AttachmentFileSerializer(NoNullSerializer):
    title = serializers.CharField()
    url = serializers.CharField()
    preview_image_url = serializers.CharField()
    file_type = serializers.CharField()
    id = serializers.CharField()


class CRNewTimelineSerializer(BaseTimelineSerializer):
    date_sort = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    crid = serializers.CharField()
    category = serializers.SerializerMethodField()
    subcategory = serializers.CharField()
    finding = serializers.CharField(source='final_finding_display')
    outcome = serializers.CharField(source='final_outcome')
    coaccused = serializers.IntegerField(source='coaccused_count')
    attachments = AttachmentFileSerializer(many=True, source='filtered_attachments')
    point = serializers.SerializerMethodField()
    victims = VictimSerializer(many=True)

    def get_date_sort(self, obj):
        return obj.allegation.incident_date.date()

    def get_date(self, obj):
        return obj.allegation.incident_date.date().strftime(format='%Y-%m-%d')

    def get_category(self, obj):
        return obj.category if obj.category else 'Unknown'

    def get_kind(self, obj):
        return 'CR'

    def get_priority_sort(self, obj):
        return 30

    def get_point(self, obj):
        try:
            return {
                'lon': obj.allegation.point.x,
                'lat': obj.allegation.point.y
            }
        except AttributeError:
            return None


class AwardNewTimelineSerializer(BaseTimelineSerializer):
    date_sort = serializers.DateField(source='start_date', format=None)
    date = serializers.DateField(source='start_date', format='%Y-%m-%d')
    award_type = serializers.CharField()

    def get_kind(self, obj):
        return 'AWARD'

    def get_priority_sort(self, obj):
        return 40


class TRRNewTimelineSerializer(BaseTimelineSerializer):
    trr_id = serializers.IntegerField(source='id')
    date_sort = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    taser = serializers.NullBooleanField()
    firearm_used = serializers.NullBooleanField()
    point = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return 'FORCE'

    def get_priority_sort(self, obj):
        return 50

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


class OfficerCoaccusalSerializer(OfficerCardSerializer):
    coaccusal_count = serializers.IntegerField()
