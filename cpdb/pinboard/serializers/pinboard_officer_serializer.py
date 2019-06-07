from rest_framework import serializers

from officers.serializers.response_serializers import OfficerInfoSerializer


class PinboardOfficerSerializer(OfficerInfoSerializer):
    complaint_count = serializers.IntegerField(source='allegation_count')
