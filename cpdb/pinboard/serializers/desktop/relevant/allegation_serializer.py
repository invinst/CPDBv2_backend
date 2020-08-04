from rest_framework import serializers

from ..common import (
    AllegationSerializer as BaseAllegationSerializer,
    OfficerRowSerializer
)


class AllegationSerializer(BaseAllegationSerializer):
    coaccused = serializers.SerializerMethodField()

    def get_coaccused(self, allegation):
        coaccused = [
            officer_allegation.officer
            for officer_allegation
            in allegation.officerallegation_set.select_related('officer').order_by('-officer__allegation_count')
        ]
        return OfficerRowSerializer(coaccused, many=True).data
