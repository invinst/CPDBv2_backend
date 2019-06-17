from officers.serializers.response_serializers import PoliceUnitSerializer
from ..common import OfficerSerializer as BaseOfficerSerializer


class OfficerSerializer(BaseOfficerSerializer):
    unit = PoliceUnitSerializer(source='last_unit')
