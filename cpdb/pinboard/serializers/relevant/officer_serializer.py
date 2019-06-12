from rest_framework import serializers

from ..common import OfficerSerializer as BaseOfficerSerializer


class OfficerSerializer(BaseOfficerSerializer):
    coaccusal_count = serializers.IntegerField(allow_null=True)
    unit = serializers.SerializerMethodField()

    def get_unit(self, obj):
        return {
            'id': obj.unit_id,
            'unit_name': obj.unit_name,
            'description': obj.unit_description,
            'long_unit_name': f'Unit {obj.unit_name}' if obj.unit_name else 'Unit'
        }
