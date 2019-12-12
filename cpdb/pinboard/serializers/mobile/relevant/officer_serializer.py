from rest_framework import serializers

from ..common import OfficerMobileSerializer as BaseOfficerMobileSerializer


class OfficerMobileSerializer(BaseOfficerMobileSerializer):
    allegation_count = serializers.IntegerField()
    coaccusal_count = serializers.IntegerField(allow_null=True)
