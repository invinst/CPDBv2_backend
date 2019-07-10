from rest_framework import serializers

from ..common import (
    AllegationSerializer as BaseAllegationSerializer,
    OfficerRowSerializer
)


class AllegationSerializer(BaseAllegationSerializer):
    coaccused = serializers.SerializerMethodField()

    def get_coaccused(self, obj):
        coaccused = [officer_allegation.officer for officer_allegation in obj.prefetched_officer_allegations]
        return OfficerRowSerializer(coaccused, many=True).data
