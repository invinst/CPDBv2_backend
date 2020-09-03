import pytz

from rest_framework import serializers

from shared.serializer import NoNullSerializer


class TopLawsuitSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    case_no = serializers.CharField()
    summary = serializers.CharField()
    primary_cause = serializers.CharField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)
