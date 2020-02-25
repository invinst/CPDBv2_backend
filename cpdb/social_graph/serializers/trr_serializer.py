from rest_framework import serializers

from shared.serializer import NoNullSerializer


class TRRSerializer(NoNullSerializer):
    trr_id = serializers.IntegerField(source='id')
    date = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()
    taser = serializers.NullBooleanField()
    firearm_used = serializers.NullBooleanField()
    point = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return 'FORCE'

    def get_date(self, obj):
        return obj.trr_datetime.date().strftime('%Y-%m-%d')

    def get_point(self, obj):
        try:
            return {
                'lon': obj.point.x,
                'lat': obj.point.y
            }
        except AttributeError:
            return None
