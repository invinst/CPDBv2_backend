from rest_framework import serializers


class OfficerCardSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    complaint_count = serializers.IntegerField(source='allegation_count')
    sustained_count = serializers.IntegerField()
    birth_year = serializers.IntegerField()
    complaint_percentile = serializers.SerializerMethodField()
    race = serializers.CharField()
    gender = serializers.CharField()
    percentile = serializers.SerializerMethodField()

    def get_complaint_percentile(self, obj):
        return obj.percentiles[-1].to_dict()['percentile_allegation'] if obj.percentiles else None

    def get_percentile(self, obj):
        return obj.percentiles[-1].to_dict() if obj.percentiles else []
