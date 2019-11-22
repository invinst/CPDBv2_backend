from rest_framework import serializers

from shared.serializer import NoNullSerializer


class TRRSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    type = serializers.SerializerMethodField()

    def get_type(self, obj):
        return 'TRR'
