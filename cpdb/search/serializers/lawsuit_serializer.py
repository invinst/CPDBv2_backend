from rest_framework import serializers

import pytz

from shared.serializer import NoNullSerializer


class LawsuitRSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    case_no = serializers.CharField()
    primary_cause = serializers.CharField()
    summary = serializers.CharField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)
    type = serializers.SerializerMethodField()

    def get_type(self, obj):
        return 'LAWSUIT'
