import pytz

from rest_framework import serializers

from shared.serializer import NoNullSerializer, OfficerPercentileSerializer


class OfficerSerializer(OfficerPercentileSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    allegation_count = serializers.IntegerField()


class PlaintiffSerializer(NoNullSerializer):
    name = serializers.CharField()


class LawsuitSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    case_no = serializers.CharField()
    summary = serializers.CharField()
    primary_cause = serializers.CharField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)
    address = serializers.CharField()
    location = serializers.CharField()
    plaintiffs = PlaintiffSerializer(many=True)
    officers = OfficerSerializer(many=True)
    total_payments = serializers.DecimalField(max_digits=16, decimal_places=2, allow_null=True)
    to = serializers.CharField(source='v2_to')
