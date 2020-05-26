from rest_framework import serializers

from shared.serializer import NoNullSerializer, OfficerPercentileSerializer


class RacePopulationSerializer(serializers.Serializer):
    race = serializers.CharField()
    count = serializers.IntegerField()


class OfficerMostComplaintsSerializer(OfficerPercentileSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='full_name')
    count = serializers.IntegerField(source='allegation_count')


class VictimSerializer(NoNullSerializer):
    gender = serializers.CharField(source='gender_display')
    race = serializers.CharField()
    age = serializers.IntegerField()


class BaseOfficerSerializer(OfficerPercentileSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    allegation_count = serializers.IntegerField()


class TRROfficerSerializer(BaseOfficerSerializer):
    pass


class CoaccusedSerializer(BaseOfficerSerializer):
    pass


class AttachmentFileSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    text_content = serializers.CharField()
