from rest_framework import serializers


class OfficerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    allegation_count = serializers.IntegerField()
    name = serializers.CharField(source='full_name')
