from rest_framework import serializers

from shared.serializer import OfficerPercentileSerializer


class OfficerRowMobileSerializer(OfficerPercentileSerializer):
    id = serializers.IntegerField()
    rank = serializers.CharField()
    full_name = serializers.CharField()
    coaccusal_count = serializers.IntegerField(allow_null=True)


class OfficerMobileSerializer(OfficerPercentileSerializer):
    id = serializers.IntegerField()
    rank = serializers.CharField()
    full_name = serializers.CharField()
