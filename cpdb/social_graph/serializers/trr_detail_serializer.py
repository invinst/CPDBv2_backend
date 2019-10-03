from rest_framework import serializers

from shared.serializer import NoNullSerializer
from social_graph.serializers.officer_percentile_serializer import OfficerPercentileSerializer


class CoaccusedSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    allegation_count = serializers.IntegerField()
    percentile = serializers.SerializerMethodField()

    def get_percentile(self, obj):
        return OfficerPercentileSerializer(obj).data


class TRRDetailSerializer(NoNullSerializer):
    kind = serializers.SerializerMethodField()
    trr_id = serializers.IntegerField(source='id')
    to = serializers.CharField(source='v2_to')
    taser = serializers.NullBooleanField()
    firearm_used = serializers.NullBooleanField()
    date = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    officer = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return 'FORCE'

    def get_date(self, obj):
        return obj.trr_datetime.date().strftime(format='%Y-%m-%d')

    def get_address(self, obj):
        return ' '.join(filter(None, [obj.block, obj.street]))

    def get_officer(self, obj):
        return CoaccusedSerializer(obj.officer).data
