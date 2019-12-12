import pytz
from rest_framework import serializers

from shared.serializer import NoNullSerializer


class AllegationSerializer(NoNullSerializer):
    crid = serializers.CharField()
    category = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)

    def get_category(self, obj):
        try:
            return obj.most_common_category.category
        except AttributeError:
            return 'Unknown'
