from collections import OrderedDict

from rest_framework import serializers


class NoNullSerializer(serializers.Serializer):
    def to_representation(self, instance):
        representation = super(NoNullSerializer, self).to_representation(instance)
        return OrderedDict((key, value) for (key, value) in representation.items() if value is not None)
