from collections import OrderedDict

from rest_framework import serializers


class NoNullSerializer(serializers.Serializer):
    def to_representation(self, instance):
        representation = super(NoNullSerializer, self).to_representation(instance)
        return OrderedDict((key, value) for (key, value) in representation.items() if value is not None)


class OfficerPercentileSerializer(NoNullSerializer):
    percentile_allegation = serializers.DecimalField(
        source='complaint_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_trr = serializers.DecimalField(
        source='trr_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation_civilian = serializers.DecimalField(
        source='civilian_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation_internal = serializers.DecimalField(
        source='internal_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4)


class OfficerYearlyPercentileSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    year = serializers.IntegerField()
    percentile_allegation = serializers.DecimalField(
        allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation_civilian = serializers.DecimalField(
        allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_allegation_internal = serializers.DecimalField(
        allow_null=True, read_only=True, max_digits=6, decimal_places=4)
    percentile_trr = serializers.DecimalField(
        allow_null=True, read_only=True, max_digits=6, decimal_places=4)
