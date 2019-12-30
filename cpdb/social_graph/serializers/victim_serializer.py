from rest_framework import serializers

from shared.serializer import NoNullSerializer


class VictimSerializer(NoNullSerializer):
    gender = serializers.CharField(source='gender_display')
    race = serializers.CharField()
    age = serializers.IntegerField()
