from rest_framework import serializers

from shared.serializer import NoNullSerializer, OfficerPercentileSerializer


class CoaccusedSerializer(OfficerPercentileSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    allegation_count = serializers.IntegerField()


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
        return obj.trr_datetime.date().strftime('%Y-%m-%d')

    def get_address(self, obj):
        return ' '.join(filter(None, [obj.block, obj.street]))

    def get_officer(self, obj):
        return CoaccusedSerializer(obj.officer).data
