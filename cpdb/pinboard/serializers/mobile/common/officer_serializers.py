from rest_framework import serializers

from shared.serializer import OfficerPercentileSerializer


class OfficerRowMobileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    rank = serializers.CharField()
    full_name = serializers.CharField()
    coaccusal_count = serializers.IntegerField(allow_null=True)
    percentile = serializers.SerializerMethodField()

    def get_percentile(self, obj):
        return OfficerPercentileSerializer(obj).data


class OfficerMobileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    rank = serializers.CharField()
    full_name = serializers.CharField()
    percentile = serializers.SerializerMethodField()

    def get_percentile(self, obj):
        return OfficerPercentileSerializer(obj).data
