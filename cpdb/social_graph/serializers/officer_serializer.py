from rest_framework import serializers

from shared.serializer import NoNullSerializer
from social_graph.serializers.officer_percentile_serializer import OfficerPercentileSerializer


class OfficerSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()

    percentile = serializers.SerializerMethodField()

    def get_percentile(self, obj):
        return OfficerPercentileSerializer(obj).data
