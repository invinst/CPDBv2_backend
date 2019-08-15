from rest_framework import serializers

from shared.serializer import NoNullSerializer, LightweightOfficerPercentileSerializer


class CoaccusedSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    complaint_count = serializers.IntegerField(source='allegation_count')
    sustained_count = serializers.IntegerField()
    birth_year = serializers.IntegerField()
    complaint_percentile = serializers.FloatField(
        read_only=True, allow_null=True
    )
    race = serializers.CharField()
    gender = serializers.CharField(source='gender_display')
    rank = serializers.CharField()
    percentile = serializers.SerializerMethodField()

    def get_percentile(self, obj):
        return LightweightOfficerPercentileSerializer(obj).data
