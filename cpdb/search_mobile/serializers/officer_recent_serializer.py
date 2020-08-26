from rest_framework import serializers

from shared.serializer import NoNullSerializer


class OfficerRecentSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='full_name')
    badge = serializers.CharField(source='current_badge')
    type = serializers.SerializerMethodField()

    def get_type(self, obj):
        return 'OFFICER'
