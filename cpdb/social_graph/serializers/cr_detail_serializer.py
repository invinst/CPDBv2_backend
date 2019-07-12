from rest_framework import serializers

from shared.serializer import NoNullSerializer
from social_graph.serializers.victim_serializer import VictimSerializer
from social_graph.serializers.officer_percentile_serializer import OfficerPercentileSerializer


class CoaccusedSerializer(NoNullSerializer):
    id = serializers.IntegerField(source='officer.id')
    full_name = serializers.CharField(source='officer.full_name')
    allegation_count = serializers.IntegerField(source='officer.allegation_count')
    percentile = serializers.SerializerMethodField()

    def get_percentile(self, obj):
        return OfficerPercentileSerializer(obj.officer).data


class CRDetailSerializer(NoNullSerializer):
    kind = serializers.SerializerMethodField()
    crid = serializers.CharField()
    to = serializers.CharField(source='v2_to')
    category = serializers.SerializerMethodField()
    subcategory = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    address = serializers.CharField()
    victims = VictimSerializer(many=True)
    coaccused = CoaccusedSerializer(many=True, source='officer_allegations')

    def get_kind(self, obj):
        return 'CR'

    def get_category(self, obj):
        return obj.most_common_category.category if obj.most_common_category else 'Unknown'

    def get_subcategory(self, obj):
        return obj.most_common_category.allegation_name if obj.most_common_category else 'Unknown'
