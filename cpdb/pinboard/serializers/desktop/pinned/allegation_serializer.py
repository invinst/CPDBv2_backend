from rest_framework import serializers

from cr.serializers.cr_response_serializers import CoaccusedSerializer
from ..common import AllegationSerializer as BaseAllegationSerializer


class AllegationSerializer(BaseAllegationSerializer):
    coaccused = serializers.SerializerMethodField()

    def get_coaccused(self, obj):
        officer_allegations = obj.officer_allegations.prefetch_related(
            'officer',
            'officerallegationfinding_set__allegation_category'
        )
        return CoaccusedSerializer(officer_allegations, many=True).data
