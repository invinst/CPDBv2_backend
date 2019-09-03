from rest_framework import serializers

from shared.serializer import NoNullSerializer


class ExamplePinboardSerializer(NoNullSerializer):
    id = serializers.CharField(min_length=8, max_length=8, read_only=True, source='pinboard.id')
    title = serializers.CharField(source='pinboard.title')
    description = serializers.CharField(source='pinboard.description')
