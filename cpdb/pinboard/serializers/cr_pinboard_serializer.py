from rest_framework import serializers

from shared.serializer import NoNullSerializer
from .common import VictimSerializer


class CRPinboardSerializer(NoNullSerializer):
    date = serializers.SerializerMethodField()
    crid = serializers.CharField()
    category = serializers.SerializerMethodField()
    coaccused_count = serializers.IntegerField()
    kind = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()
    victims = VictimSerializer(many=True)

    def get_kind(self, obj):
        return 'CR'

    def get_category(self, obj):
        return obj.most_common_category.category if obj.most_common_category else 'Unknown'

    def get_date(self, obj):
        return obj.incident_date.date().strftime(format='%Y-%m-%d')

    def get_point(self, obj):
        try:
            return {
                'lon': obj.point.x,
                'lat': obj.point.y
            }
        except AttributeError:
            return None
