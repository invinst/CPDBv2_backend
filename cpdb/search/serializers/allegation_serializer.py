from rest_framework import serializers

import pytz

from shared.serializer import NoNullSerializer


class AllegationSerializer(NoNullSerializer):
    id = serializers.CharField(source='crid')
    crid = serializers.CharField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)
    type = serializers.SerializerMethodField()

    def get_type(self, obj):
        return 'CR'
