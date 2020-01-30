from rest_framework import serializers

from shared.serializer import NoNullSerializer


class CRSerializer(NoNullSerializer):
    date = serializers.SerializerMethodField()
    crid = serializers.CharField()
    category = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return 'CR'

    def get_category(self, obj):
        return obj.most_common_category.category if obj.most_common_category else 'Unknown'

    def get_date(self, obj):
        return obj.incident_date.date().strftime('%Y-%m-%d')

    def get_point(self, obj):
        try:
            return {
                'lon': obj.point.x,
                'lat': obj.point.y
            }
        except AttributeError:
            return None
