from rest_framework import serializers

from .lawsuit_serializer import LawsuitSerializer


class LawsuitRecentSerializer(LawsuitSerializer):
    type = serializers.SerializerMethodField()

    def get_type(self, obj):
        return 'LAWSUIT'
