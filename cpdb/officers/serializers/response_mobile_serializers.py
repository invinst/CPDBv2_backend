from rest_framework import serializers

from shared.serializer import NoNullSerializer, OfficerPercentileSerializer, OfficerYearlyPercentileSerializer


class PoliceUnitMobileSerializer(NoNullSerializer):
    unit_id = serializers.IntegerField(source='id')
    unit_name = serializers.CharField()
    description = serializers.CharField()


class OfficerInfoMobileSerializer(NoNullSerializer):
    officer_id = serializers.IntegerField(source='id')
    full_name = serializers.CharField()
    unit = PoliceUnitMobileSerializer(source='last_unit')
    date_of_appt = serializers.DateField(source='appointed_date', format='%Y-%m-%d')
    date_of_resignation = serializers.DateField(source='resignation_date', format='%Y-%m-%d')
    active = serializers.SerializerMethodField()
    rank = serializers.CharField()
    race = serializers.CharField()
    birth_year = serializers.IntegerField()
    badge = serializers.SerializerMethodField()
    historic_badges = serializers.ListField(child=serializers.CharField())
    gender = serializers.CharField(source='gender_display')
    percentiles = serializers.SerializerMethodField()

    allegation_count = serializers.IntegerField()
    percentile_allegation = serializers.DecimalField(
        source='complaint_percentile', max_digits=6, decimal_places=4, allow_null=True
    )
    percentile_trr = serializers.DecimalField(source='trr_percentile', max_digits=6, decimal_places=4, allow_null=True)
    honorable_mention_count = serializers.IntegerField()
    sustained_count = serializers.IntegerField()
    unsustained_count = serializers.IntegerField()
    discipline_count = serializers.IntegerField()
    civilian_compliment_count = serializers.IntegerField()
    trr_count = serializers.IntegerField()
    major_award_count = serializers.IntegerField()
    honorable_mention_percentile = serializers.DecimalField(max_digits=6, decimal_places=4, allow_null=True)

    def get_percentiles(self, obj):
        yearly_percentiles = obj.officeryearlypercentile_set.order_by('year')
        return OfficerYearlyPercentileSerializer(yearly_percentiles, many=True).data

    def get_active(self, obj):
        return obj.get_active_display()

    def get_badge(self, obj):
        return obj.current_badge or ''


class BaseTimelineMobileSerializer(NoNullSerializer):
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


class RankChangeNewTimelineMobileSerializer(BaseTimelineMobileSerializer):
    date_sort = serializers.DateField(source='spp_date', format=None)
    date = serializers.DateField(source='spp_date', format='%Y-%m-%d')

    def get_kind(self, obj):
        return 'RANK_CHANGE'

    def get_priority_sort(self, obj):
        return 25

    def get_rank(self, obj):
        return obj.rank


class JoinedNewTimelineMobileSerializer(BaseTimelineMobileSerializer):
    date_sort = serializers.DateField(source='appointed_date', format=None)
    date = serializers.DateField(source='appointed_date', format='%Y-%m-%d')

    def get_kind(self, obj):
        return 'JOINED'

    def get_priority_sort(self, obj):
        return 10


class UnitChangeNewTimelineMobileSerializer(BaseTimelineMobileSerializer):
    date_sort = serializers.DateField(source='effective_date', format=None)
    date = serializers.DateField(source='effective_date', format='%Y-%m-%d')

    def get_kind(self, obj):
        return 'UNIT_CHANGE'

    def get_priority_sort(self, obj):
        return 20


class VictimMobileSerializer(NoNullSerializer):
    gender = serializers.CharField(source='gender_display')
    race = serializers.CharField()
    age = serializers.IntegerField()


class AttachmentFileMobileSerializer(NoNullSerializer):
    title = serializers.CharField()
    url = serializers.CharField()
    preview_image_url = serializers.CharField()
    file_type = serializers.CharField()
    id = serializers.CharField()


class CRNewTimelineMobileSerializer(BaseTimelineMobileSerializer):
    date_sort = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    crid = serializers.CharField()
    category = serializers.SerializerMethodField()
    subcategory = serializers.CharField()
    finding = serializers.CharField(source='final_finding_display')
    outcome = serializers.CharField(source='final_outcome')
    coaccused = serializers.IntegerField(source='coaccused_count')
    attachments = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()
    victims = VictimMobileSerializer(many=True)

    def get_date_sort(self, obj):
        return obj.allegation.incident_date.date()

    def get_date(self, obj):
        return obj.allegation.incident_date.date().strftime('%Y-%m-%d')

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

    def get_attachments(self, obj):
        return AttachmentFileMobileSerializer(obj.allegation.prefetch_filtered_attachments, many=True).data


class AwardNewTimelineMobileSerializer(BaseTimelineMobileSerializer):
    date_sort = serializers.DateField(source='start_date', format=None)
    date = serializers.DateField(source='start_date', format='%Y-%m-%d')
    award_type = serializers.CharField()

    def get_kind(self, obj):
        return 'AWARD'

    def get_priority_sort(self, obj):
        return 40


class TRRNewTimelineMobileSerializer(BaseTimelineMobileSerializer):
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
        return obj.trr_datetime.date().strftime('%Y-%m-%d')

    def get_point(self, obj):
        try:
            return {
                'lon': obj.point.x,
                'lat': obj.point.y
            }
        except AttributeError:
            return None


class LawsuitNewTimelineMobileSerializer(BaseTimelineMobileSerializer):
    date_sort = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    case_no = serializers.CharField()
    primary_cause = serializers.CharField()
    attachments = AttachmentFileMobileSerializer(source='attachment_files', many=True)

    def get_date_sort(self, obj):
        return obj.incident_date.date()

    def get_date(self, obj):
        return obj.incident_date.date().strftime('%Y-%m-%d')

    def get_kind(self, obj):
        return 'LAWSUIT'

    def get_priority_sort(self, obj):
        return 50


class OfficerPercentileMobileSerializer(NoNullSerializer):
    percentile_trr = serializers.DecimalField(
        source='trr_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation_civilian = serializers.DecimalField(
        source='civilian_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation_internal = serializers.DecimalField(
        source='internal_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)


class CoaccusalCardMobileSerializer(OfficerPercentileSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    rank = serializers.CharField()
    coaccusal_count = serializers.IntegerField()


class OfficerCardMobileSerializer(OfficerPercentileSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    complaint_count = serializers.IntegerField(source='allegation_count')
