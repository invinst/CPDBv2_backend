from rest_framework import serializers

from ..common import OfficerMobileSerializer as BaseOfficerMobileSerializer


class OfficerMobileSerializer(BaseOfficerMobileSerializer):
    complaint_count = serializers.IntegerField(source='allegation_count')
