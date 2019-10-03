from rest_framework import serializers

import pytz

from shared.serializer import NoNullSerializer


class AccusedSerializer(NoNullSerializer):
    officer_id_1 = serializers.IntegerField()
    officer_id_2 = serializers.IntegerField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)
    accussed_count = serializers.IntegerField()
