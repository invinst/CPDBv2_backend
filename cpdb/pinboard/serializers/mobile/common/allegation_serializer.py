from rest_framework import serializers

from shared.serializer import NoNullSerializer


class AllegationMobileSerializer(NoNullSerializer):
    crid = serializers.CharField()
    point = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    category = serializers.SerializerMethodField()

    def get_point(self, obj):
        return {'lon': obj.point.x, 'lat': obj.point.y} if obj.point is not None else None

    def get_category(self, obj):
        try:
            return obj.most_common_category.category
        except AttributeError:
            return 'Unknown'
