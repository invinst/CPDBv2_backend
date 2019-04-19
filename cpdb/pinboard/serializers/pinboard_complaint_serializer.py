from rest_framework import serializers

from data.models import Allegation


class PinboardComplaintSerializer(serializers.ModelSerializer):
    most_common_category = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')

    def get_point(self, obj):
        return {'lon': obj.point.x, 'lat': obj.point.y} if obj.point is not None else None

    def get_most_common_category(self, obj):
        return obj.most_common_category.category if obj.most_common_category is not None else ''

    class Meta:
        model = Allegation
        fields = (
            'crid',
            'incident_date',
            'point',
            'most_common_category'
        )
