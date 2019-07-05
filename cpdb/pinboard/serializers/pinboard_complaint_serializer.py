from rest_framework import serializers

from cr.serializers.cr_response_serializers import CoaccusedSerializer, VictimSerializer
from data.models import Allegation


class PinboardComplaintSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()
    most_common_category = serializers.SerializerMethodField()
    coaccused = serializers.SerializerMethodField()
    sub_category = serializers.SerializerMethodField()
    to = serializers.SerializerMethodField()
    victims = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')

    def get_coaccused(self, obj):
        return CoaccusedSerializer(obj.officer_allegations, many=True).data

    def get_victims(self, obj):
        return VictimSerializer(obj.victims, many=True).data

    def get_address(self, obj):
        if obj.old_complaint_address is not None:
            return obj.old_complaint_address
        result = ' '.join(list(filter(None, [obj.add1, obj.add2])))
        return ', '.join(list(filter(None, [result, obj.city])))

    def get_point(self, obj):
        return {'lon': obj.point.x, 'lat': obj.point.y} if obj.point is not None else None

    def get_most_common_category(self, obj):
        return obj.most_common_category.category if obj.most_common_category is not None else 'Unknown'

    def get_sub_category(self, obj):
        return obj.most_common_category.allegation_name if obj.most_common_category is not None else 'Unknown'

    def get_to(self, obj):
        return f'/complaint/{obj.crid}/'

    class Meta:
        model = Allegation
        fields = (
            'address',
            'coaccused',
            'sub_category',
            'to',
            'crid',
            'incident_date',
            'point',
            'most_common_category',
            'victims',
        )
