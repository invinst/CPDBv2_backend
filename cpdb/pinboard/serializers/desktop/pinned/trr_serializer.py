from rest_framework import serializers

from trr.models import TRR


class TRRSerializer(serializers.ModelSerializer):
    trr_datetime = serializers.DateTimeField(format='%Y-%m-%d')
    point = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    def get_point(self, obj):
        return {'lon': obj.point.x, 'lat': obj.point.y} if obj.point is not None else None

    def get_category(self, obj):
        return obj.force_types[0] if len(obj.force_types) > 0 else 'Unknown'

    class Meta:
        model = TRR
        fields = (
            'id',
            'trr_datetime',
            'category',
            'point',
        )
