from rest_framework import serializers

import pytz

from shared.serializer import NoNullSerializer


class TRRSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    force_type = serializers.CharField(max_length=255, source='top_force_type')
    trr_datetime = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)
    type = serializers.SerializerMethodField()

    def get_type(self, obj):
        return 'TRR'
