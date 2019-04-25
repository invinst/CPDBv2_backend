from rest_framework import serializers

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


class OfficerDetailSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()

    percentile = serializers.SerializerMethodField()

    def get_percentile(self, obj):
        return OfficerPercentileSerializer(obj).data


class AllegationCategorySerializer(NoNullSerializer):
    category = serializers.CharField()
    allegation_name = serializers.CharField()


class AllegationSerializer(NoNullSerializer):
    crid = serializers.CharField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    most_common_category = AllegationCategorySerializer()


class AccussedSerializer(NoNullSerializer):
    officer_id_1 = serializers.IntegerField()
    officer_id_2 = serializers.IntegerField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    accussed_count = serializers.IntegerField()
