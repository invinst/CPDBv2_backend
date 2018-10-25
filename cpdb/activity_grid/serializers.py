from rest_framework import serializers


# Todo: This should inherit from officer's OfficerCardSerializer
# Todo so, ActivityGridViewSet should be refactored to query directly from Postgress instead of ES
class OfficerCardSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    complaint_count = serializers.IntegerField(source='allegation_count')
    sustained_count = serializers.IntegerField()
    birth_year = serializers.IntegerField()
    complaint_percentile = serializers.FloatField(read_only=True, allow_null=True)
    race = serializers.CharField()
    gender = serializers.CharField()
    rank = serializers.CharField()
    percentile = serializers.SerializerMethodField()

    def get_percentile(self, obj):
        return obj.percentiles[-1].to_dict() if obj.percentiles else None


class SimpleCardSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    birth_year = serializers.IntegerField()
    race = serializers.CharField()
    gender = serializers.CharField()
    percentile = serializers.SerializerMethodField()
    rank = serializers.CharField()

    def get_percentile(self, obj):
        return obj.percentiles[-1].to_dict() if obj.percentiles else None
