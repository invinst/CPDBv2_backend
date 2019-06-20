from rest_framework import serializers

from data.models import PoliceUnit
from shared.serializer import NoNullSerializer


class VictimSerializer(NoNullSerializer):
    gender = serializers.CharField(source='gender_display')
    race = serializers.CharField()
    age = serializers.IntegerField()


class OfficerPercentileSerializer(NoNullSerializer):
    percentile_trr = serializers.DecimalField(
        source='trr_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation_civilian = serializers.DecimalField(
        source='civilian_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation_internal = serializers.DecimalField(
        source='internal_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)


class OfficerSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()

    percentile = serializers.SerializerMethodField()

    def get_percentile(self, obj):
        return OfficerPercentileSerializer(obj).data


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliceUnit
        fields = ['id', 'unit_name', 'description']


class OfficerDetailSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    rank = serializers.CharField()
    badge = serializers.CharField(source='current_badge')
    race = serializers.CharField()
    birth_year = serializers.CharField()
    unit = UnitSerializer(source='last_unit', allow_null=True, read_only=True)
    gender = serializers.CharField()
    allegation_count = serializers.IntegerField()
    sustained_count = serializers.IntegerField()
    honorable_mention_count = serializers.IntegerField()
    major_award_count = serializers.IntegerField()
    trr_count = serializers.IntegerField()
    discipline_count = serializers.IntegerField()
    civilian_compliment_count = serializers.IntegerField()
    resignation_date = serializers.DateTimeField(format='%Y-%m-%d')
    appointed_date = serializers.DateTimeField(format='%Y-%m-%d')
    percentile = serializers.SerializerMethodField()
    honorable_mention_percentile = serializers.FloatField(allow_null=True, read_only=True)

    def get_percentile(self, obj):
        return OfficerPercentileSerializer(obj).data


class AllegationCategorySerializer(NoNullSerializer):
    category = serializers.CharField()
    allegation_name = serializers.CharField()


class AttachmentFileSerializer(NoNullSerializer):
    title = serializers.CharField()
    url = serializers.CharField()
    preview_image_url = serializers.CharField()
    file_type = serializers.CharField()
    id = serializers.CharField()


class OfficerAllegationPercentileSerializer(serializers.Serializer):
    percentile_trr = serializers.DecimalField(
        source='officer.trr_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation = serializers.DecimalField(
        source='officer.complaint_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation_civilian = serializers.DecimalField(
        source='officer.civilian_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4
    )
    percentile_allegation_internal = serializers.DecimalField(
        source='officer.internal_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4
    )


class CoaccusedSerializer(NoNullSerializer):
    id = serializers.IntegerField(source='officer.id')
    full_name = serializers.CharField(source='officer.full_name')
    complaint_count = serializers.IntegerField(source='officer.allegation_count')
    sustained_count = serializers.IntegerField(source='officer.sustained_count')
    birth_year = serializers.IntegerField(source='officer.birth_year')
    complaint_percentile = serializers.FloatField(
        read_only=True, allow_null=True, source='officer.complaint_percentile'
    )
    recommended_outcome = serializers.CharField(source='recc_outcome')
    final_outcome = serializers.CharField()
    final_finding = serializers.CharField(source='final_finding_display')
    category = serializers.CharField()
    disciplined = serializers.NullBooleanField()
    race = serializers.CharField(source='officer.race')
    gender = serializers.CharField(source='officer.gender_display')
    rank = serializers.CharField(source='officer.rank')
    percentile = serializers.SerializerMethodField()

    def get_percentile(self, obj):
        return OfficerAllegationPercentileSerializer(obj).data


class AllegationSerializer(NoNullSerializer):
    kind = serializers.SerializerMethodField()
    crid = serializers.CharField()
    to = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    subcategory = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    address = serializers.CharField()
    victims = VictimSerializer(many=True)
    coaccused = serializers.SerializerMethodField()
    attachments = AttachmentFileSerializer(source='prefetch_filtered_attachment_files', many=True)
    officer_ids = serializers.SerializerMethodField()

    def get_officer_ids(self, obj):
        return [officer_allegation.officer_id for officer_allegation in obj.officer_allegations]

    def get_kind(self, obj):
        return 'CR'

    def get_to(self, obj):
        return f'/complaint/{obj.crid}/'

    def get_category(self, obj):
        return obj.most_common_category.category if obj.most_common_category else 'Unknown'

    def get_subcategory(self, obj):
        return obj.most_common_category.allegation_name if obj.most_common_category else 'Unknown'

    def get_coaccused(self, obj):
        officer_allegations = obj.officer_allegations

        return CoaccusedSerializer(officer_allegations, many=True).data


class AccussedSerializer(NoNullSerializer):
    officer_id_1 = serializers.IntegerField()
    officer_id_2 = serializers.IntegerField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    accussed_count = serializers.IntegerField()
