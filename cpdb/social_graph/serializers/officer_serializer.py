from rest_framework import serializers

from shared.serializer import OfficerPercentileSerializer


class OfficerSerializer(OfficerPercentileSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
