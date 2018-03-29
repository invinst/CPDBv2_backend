from rest_framework import serializers

from officers.serializers import OfficerYearlyPercentileSerializer


class OfficerCardSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    complaint_count = serializers.SerializerMethodField()
    sustained_count = serializers.SerializerMethodField()
    birth_year = serializers.IntegerField()
    # complaint_percentile = serializers.FloatField()
    race = serializers.CharField()
    gender = serializers.CharField(source='gender_display')
    percentile = OfficerYearlyPercentileSerializer(read_only=True)

    def get_complaint_count(self, obj):
        return obj.complaint_count_metric

    def get_sustained_count(self, obj):
        return obj.sustained_count_metric
