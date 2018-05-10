from rest_framework import serializers


class RacePopulationSerializer(serializers.Serializer):
    race = serializers.CharField()
    count = serializers.IntegerField()
