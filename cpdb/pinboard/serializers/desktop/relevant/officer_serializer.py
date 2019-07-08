from rest_framework import serializers

from shared.serializer import NoNullSerializer
from ..common import OfficerSerializer as BaseOfficerSerializer


class UnitSerializer(NoNullSerializer):
    id = serializers.IntegerField(source='unit_id')
    unit_name = serializers.CharField()
    description = serializers.CharField(source='unit_description')
    long_unit_name = serializers.SerializerMethodField()

    def get_long_unit_name(self, obj):
        return f'Unit {obj.unit_name}' if obj.unit_name else 'Unit'


class OfficerSerializer(BaseOfficerSerializer):
    coaccusal_count = serializers.IntegerField(allow_null=True)
    unit = serializers.SerializerMethodField()

    def get_unit(self, obj):
        return UnitSerializer(obj).data
