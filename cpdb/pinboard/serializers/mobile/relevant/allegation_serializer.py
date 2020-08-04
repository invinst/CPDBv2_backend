from rest_framework import serializers

from ..common import (
    AllegationMobileSerializer as BaseAllegationMobileSerializer,
    OfficerRowMobileSerializer,
)


class AllegationMobileSerializer(BaseAllegationMobileSerializer):
    officers = serializers.SerializerMethodField()

    def get_officers(self, allegation):
        officers = [
            officer_allegation.officer
            for officer_allegation
            in allegation.officerallegation_set.select_related('officer').order_by('-officer__allegation_count')
        ]
        return OfficerRowMobileSerializer(officers, many=True).data
