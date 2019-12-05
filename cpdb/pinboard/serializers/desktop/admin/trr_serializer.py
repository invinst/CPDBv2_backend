import pytz
from rest_framework import serializers

from shared.serializer import NoNullSerializer


class TRRSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    trr_datetime = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)
    category = serializers.SerializerMethodField()

    def get_category(self, obj):
        force_types = [res.force_type for res in obj.actionresponse_set.all()]
        return force_types[0] if len(force_types) > 0 else 'Unknown'
