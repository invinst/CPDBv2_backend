from rest_framework import serializers

from shared.serializer import NoNullSerializer
from social_graph.serializers.officer_percentile_serializer import OfficerPercentileSerializer


class CoaccusedSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    complaint_count = serializers.IntegerField(source='allegation_count')
    sustained_count = serializers.IntegerField()
    birth_year = serializers.IntegerField()
    complaint_percentile = serializers.FloatField(
        read_only=True, allow_null=True
    )
    race = serializers.CharField()
    gender = serializers.CharField(source='gender_display')
    rank = serializers.CharField()
    percentile = serializers.SerializerMethodField()

    def get_percentile(self, obj):
        return OfficerPercentileSerializer(obj).data


class TRRPreviewPaneSerializer(NoNullSerializer):
    kind = serializers.SerializerMethodField()
    trr_id = serializers.IntegerField(source='id')
    to = serializers.SerializerMethodField()
    taser = serializers.NullBooleanField()
    firearm_used = serializers.NullBooleanField()
    date = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    officer = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return 'FORCE'

    def get_to(self, obj):
        return f'/trr/{obj.id}/'

    def get_date(self, obj):
        return obj.trr_datetime.date().strftime(format='%Y-%m-%d')

    def get_address(self, obj):
        return ' '.join(filter(None, [obj.block, obj.street]))

    def get_officer(self, obj):
        return CoaccusedSerializer(obj.officer).data
