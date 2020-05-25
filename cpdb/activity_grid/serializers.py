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
    race = serializers.CharField(source='officer.race')
    gender = serializers.CharField(source='officer.gender_display')
    rank = serializers.CharField(source='officer.rank')
    important = serializers.BooleanField()
    null_position = serializers.IntegerField()
    last_activity = serializers.DateTimeField(default_timezone=pytz.utc)
    kind = serializers.CharField(default=RESPONSE_TYPE_SINGLE_OFFICER)

    percentile_allegation = serializers.DecimalField(
        source='officer.complaint_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4
    )
    percentile_trr = serializers.DecimalField(
        source='officer.trr_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4
    )
    percentile_allegation_civilian = serializers.DecimalField(
        source='officer.civilian_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4
    )
    percentile_allegation_internal = serializers.DecimalField(
        source='officer.internal_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4
    )


class SimpleCardSerializer(OfficerPercentileSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    birth_year = serializers.IntegerField()
    race = serializers.CharField()
    gender = serializers.CharField(source='gender_display')
    rank = serializers.CharField()
    complaint_count = serializers.IntegerField(source='allegation_count')
    sustained_count = serializers.IntegerField()


class PairCardSerializer(serializers.Serializer):
    officer1 = SimpleCardSerializer()
    officer2 = SimpleCardSerializer()
    coaccusal_count = serializers.IntegerField()
    important = serializers.BooleanField()
    null_position = serializers.IntegerField()
    last_activity = serializers.DateTimeField(default_timezone=pytz.utc)
    kind = serializers.CharField(default=RESPONSE_TYPE_COACCUSED_PAIR)
