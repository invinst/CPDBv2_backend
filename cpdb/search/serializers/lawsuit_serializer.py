import pytz

from rest_framework import serializers

from shared.serializer import NoNullSerializer


class LawsuitSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    case_no = serializers.CharField()
    summary = serializers.CharField()
    primary_cause = serializers.CharField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)
    to = serializers.CharField(source='v2_to')
