from rest_framework import serializers

import pytz

from shared.serializer import OfficerPercentileSerializer
from twitterbot.constants import RESPONSE_TYPE_COACCUSED_PAIR, RESPONSE_TYPE_SINGLE_OFFICER


class OfficerCardSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='officer.id')
    full_name = serializers.CharField(source='officer.full_name')
    complaint_count = serializers.IntegerField(source='officer.allegation_count')
    sustained_count = serializers.IntegerField(source='officer.sustained_count')
    birth_year = serializers.IntegerField(source='officer.birth_year')
    complaint_percentile = serializers.FloatField(
        source='officer.complaint_percentile',
        read_only=True,
        allow_null=True
    )
    race = serializers.CharField(source='officer.race')
    gender = serializers.CharField(source='officer.gender_display')
    rank = serializers.CharField(source='officer.rank')
    percentile = OfficerPercentileSerializer(source='officer')
    important = serializers.BooleanField()
    null_position = serializers.IntegerField()
    last_activity = serializers.DateTimeField(default_timezone=pytz.utc)
    kind = serializers.CharField(default=RESPONSE_TYPE_SINGLE_OFFICER)


class SimpleCardSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    birth_year = serializers.IntegerField()
    race = serializers.CharField()
    gender = serializers.CharField(source='gender_display')
    percentile = serializers.SerializerMethodField()
    rank = serializers.CharField()

    def get_percentile(self, obj):
        return OfficerPercentileSerializer(obj).data


class PairCardSerializer(serializers.Serializer):
    officer1 = SimpleCardSerializer()
    officer2 = SimpleCardSerializer()
    coaccusal_count = serializers.IntegerField()
    important = serializers.BooleanField()
    null_position = serializers.IntegerField()
    last_activity = serializers.DateTimeField(default_timezone=pytz.utc)
    kind = serializers.CharField(default=RESPONSE_TYPE_COACCUSED_PAIR)
