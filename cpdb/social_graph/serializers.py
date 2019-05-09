from rest_framework import serializers

from data.models import PoliceUnit
from shared.serializer import NoNullSerializer


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


class AllegationSerializer(NoNullSerializer):
    crid = serializers.CharField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    most_common_category = AllegationCategorySerializer()
    attachments = AttachmentFileSerializer(source='filtered_attachment_files', many=True)


class AccussedSerializer(NoNullSerializer):
    officer_id_1 = serializers.IntegerField()
    officer_id_2 = serializers.IntegerField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    accussed_count = serializers.IntegerField()
