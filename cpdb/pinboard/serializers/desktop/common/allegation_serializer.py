from rest_framework import serializers

from .victim_serializer import VictimSerializer


class AllegationSerializer(serializers.Serializer):
    crid = serializers.CharField()
    address = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    victims = VictimSerializer(many=True)
    point = serializers.SerializerMethodField()
    to = serializers.SerializerMethodField()
    sub_category = serializers.SerializerMethodField()

    def get_address(self, obj):
        if obj.old_complaint_address is not None:
            return obj.old_complaint_address
        result = ' '.join(list(filter(None, [obj.add1, obj.add2])))
        return ', '.join(list(filter(None, [result, obj.city])))

    def get_category(self, obj):
        try:
            return obj.most_common_category.category
        except AttributeError:
            return 'Unknown'

    def get_point(self, obj):
        if obj.point is not None:
            return {'lon': obj.point.x, 'lat': obj.point.y}

    def get_to(self, obj):
        return f'/complaint/{obj.crid}/'

    def get_sub_category(self, obj):
        return obj.most_common_category.allegation_name if obj.most_common_category is not None else 'Unknown'
