from rest_framework import serializers

from ..common import (
    AllegationMobileSerializer as BaseAllegationMobileSerializer,
    OfficerRowMobileSerializer,
)


class AllegationMobileSerializer(BaseAllegationMobileSerializer):
    officers = serializers.SerializerMethodField()

    def get_officers(self, obj):
        officers = [officer_allegation.officer for officer_allegation in obj.prefetched_officer_allegations]
        return OfficerRowMobileSerializer(officers, many=True).data
