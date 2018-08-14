from rest_framework import serializers


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


class OfficerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    allegation_count = serializers.IntegerField()
    full_name = serializers.CharField()
    percentiles = OfficerYearlyPercentileSerializer(many=True, read_only=True)
