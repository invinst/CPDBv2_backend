from rest_framework import serializers

from shared.serializer import NoNullSerializer


class RacePopulationSerializer(serializers.Serializer):
    race = serializers.CharField()
    count = serializers.IntegerField()


class OfficerMostComplaintsSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='full_name')
    count = serializers.IntegerField(source='allegation_count')
    percentile_allegation = serializers.FloatField(
        source='complaint_percentile', allow_null=True, read_only=True)
    percentile_allegation_civilian = serializers.FloatField(
        source='civilian_allegation_percentile', allow_null=True, read_only=True)
    percentile_allegation_internal = serializers.FloatField(
        source='internal_allegation_percentile', allow_null=True, read_only=True)
    percentile_trr = serializers.FloatField(
        source='trr_percentile', allow_null=True, read_only=True)


class VictimSerializer(NoNullSerializer):
    gender = serializers.CharField(source='gender_display')
    race = serializers.CharField()
    age = serializers.IntegerField()


class OfficerAllegationPercentileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    percentile_allegation = serializers.DecimalField(
        source='complaint_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4
    )
    percentile_trr = serializers.DecimalField(
        source='trr_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation_civilian = serializers.DecimalField(
        source='civilian_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4
    )
    percentile_allegation_internal = serializers.DecimalField(
        source='internal_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4
    )


class BaseOfficerSerializer(NoNullSerializer):
    id = serializers.IntegerField(source='officer.id')
    full_name = serializers.CharField(source='officer.full_name')
    percentile = serializers.SerializerMethodField()
    allegation_count = serializers.IntegerField(source='officer.allegation_count')

    def get_percentile(self, obj):
        return OfficerAllegationPercentileSerializer(obj.officer).data


class TRROfficerSerializer(BaseOfficerSerializer):
    pass


class CoaccusedSerializer(BaseOfficerSerializer):
    pass


class AttachmentFileSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    text_content = serializers.CharField()
