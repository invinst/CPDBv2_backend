from rest_framework import serializers

from shared.serializer import OfficerPercentileSerializer


class OfficerSerializer(OfficerPercentileSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='full_name')
    count = serializers.IntegerField(source='allegation_count')
