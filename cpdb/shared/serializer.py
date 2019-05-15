from collections import OrderedDict

from rest_framework import serializers

from data.constants import MAX_VISUAL_TOKEN_YEAR


class NoNullSerializer(serializers.Serializer):
    def to_representation(self, instance):
        representation = super(NoNullSerializer, self).to_representation(instance)
        return OrderedDict((key, value) for (key, value) in representation.items() if value is not None)


class OfficerPercentileSerializer(NoNullSerializer):
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
