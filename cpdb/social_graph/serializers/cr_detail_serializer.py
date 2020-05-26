from rest_framework import serializers

import pytz

from shared.serializer import NoNullSerializer
from social_graph.serializers.victim_serializer import VictimSerializer
from shared.serializer import OfficerPercentileSerializer


class CoaccusedSerializer(OfficerPercentileSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    allegation_count = serializers.IntegerField()


class CRDetailSerializer(NoNullSerializer):
    kind = serializers.SerializerMethodField()
    crid = serializers.CharField()
    to = serializers.CharField(source='v2_to')
    category = serializers.SerializerMethodField()
    subcategory = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)
    address = serializers.CharField()
    victims = VictimSerializer(many=True)
    coaccused = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return 'CR'

    def get_category(self, obj):
        return obj.most_common_category.category if obj.most_common_category else 'Unknown'

    def get_subcategory(self, obj):
        return obj.most_common_category.allegation_name if obj.most_common_category else 'Unknown'

    def get_coaccused(self, obj):
        officers = [officer_allegation.officer for officer_allegation in obj.officer_allegations]
        return CoaccusedSerializer(officers, many=True).data
