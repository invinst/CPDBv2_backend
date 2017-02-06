from rest_framework import serializers


class OfficerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    allegation_count = serializers.IntegerField()
    full_name = serializers.CharField()
    v1_url = serializers.URLField()
