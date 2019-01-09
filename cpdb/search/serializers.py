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
