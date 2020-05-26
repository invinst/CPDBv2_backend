from rest_framework import serializers

from shared.serializer import OfficerYearlyPercentileSerializer


class OfficerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    allegation_count = serializers.IntegerField()
    full_name = serializers.CharField()
    percentiles = OfficerYearlyPercentileSerializer(many=True, read_only=True)
