from rest_framework import serializers

import pytz

from shared.serializer import NoNullSerializer
from .coaccused_serializer import CoaccusedSerializer


class TRRSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    to = serializers.SerializerMethodField()
    taser = serializers.NullBooleanField()
    firearm_used = serializers.NullBooleanField()
    address = serializers.SerializerMethodField()
    officer = serializers.SerializerMethodField()
    trr_datetime = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)
    point = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    def get_point(self, obj):
        return {'lon': obj.point.x, 'lat': obj.point.y} if obj.point is not None else None

    def get_category(self, obj):
        return obj.force_types[0] if len(obj.force_types) > 0 else 'Unknown'

    def get_to(self, obj):
        return f'/trr/{obj.id}/'

    def get_address(self, obj):
        return ' '.join(filter(None, [obj.block, obj.street]))

    def get_officer(self, obj):
        return CoaccusedSerializer(obj.officer).data
