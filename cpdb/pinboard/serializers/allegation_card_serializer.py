from rest_framework import serializers

from pinboard.serializers.officer_card_serializer import OfficerCardSerializer


class AllegationCardSerializer(serializers.Serializer):
    crid = serializers.CharField()
    category = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    officers = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()

    def get_officers(self, obj):
        officers = [officer_allegation.officer for officer_allegation in obj.prefetch_officer_allegations]
        return OfficerCardSerializer(officers, many=True).data

    def get_category(self, obj):
        try:
            return obj.most_common_category.category
        except AttributeError:
            return 'Unknown'

    def get_point(self, obj):
        if obj.point is not None:
            return {'lon': obj.point.x, 'lat': obj.point.y}
        else:
            return None
