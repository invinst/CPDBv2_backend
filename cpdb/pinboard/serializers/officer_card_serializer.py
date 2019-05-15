from rest_framework import serializers

from data.models import Officer
from shared.serializer import OfficerPercentileSerializer


class OfficerCardSerializer(serializers.ModelSerializer):
    coaccusal_count = serializers.IntegerField(allow_null=True)
    percentile = serializers.SerializerMethodField()

    def get_percentile(self, obj):
        return OfficerPercentileSerializer(obj).data

    class Meta:
        model = Officer
        fields = (
            'id',
            'rank',
            'full_name',
            'coaccusal_count',
            'percentile',
        )
