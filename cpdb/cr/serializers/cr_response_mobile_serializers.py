from rest_framework import serializers

from .base import CherryPickSerializer


class InvestigatorMobileSerializer(CherryPickSerializer):
    class Meta(object):
        fields = (
            'involved_type',
            'officer_id',
            'full_name',
            'current_rank',
            'percentile_allegation_civilian',
            'percentile_allegation_internal',
            'percentile_trr'
        )


class PoliceWitnessMobileSerializer(CherryPickSerializer):
    class Meta(object):
        fields = (
            'involved_type',
            'officer_id',
            'full_name',
            'allegation_count',
            'sustained_count',
            'percentile_allegation_civilian',
            'percentile_allegation_internal',
            'percentile_trr'
        )


class CoaccusedMobileSerializer(CherryPickSerializer):
    class Meta(object):
        fields = (
            'id',
            'full_name',
            'rank',
            'final_outcome',
            'final_finding',
            'category',
            'allegation_count',
            'percentile_allegation',
            'percentile_allegation_civilian',
            'percentile_allegation_internal',
            'percentile_trr'
        )


class CRMobileSerializer(serializers.Serializer):
    crid = serializers.CharField()
    most_common_category = serializers.JSONField(required=False)
    coaccused = CoaccusedMobileSerializer(many=True, default=[])
    complainants = serializers.JSONField(default=[])
    victims = serializers.JSONField(default=[])
    summary = serializers.CharField(required=False)
    point = serializers.JSONField(required=False)
    incident_date = serializers.CharField(required=False)
    start_date = serializers.CharField(required=False)
    end_date = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    location = serializers.CharField(required=False)
    beat = serializers.CharField(required=False)
    involvements = serializers.SerializerMethodField()
    attachments = serializers.JSONField(default=[])

    def get_involvements(self, obj):
        serializer_map = {
            'investigator': InvestigatorMobileSerializer,
            'police_witness': PoliceWitnessMobileSerializer
        }
        return [
            serializer_map[involvement['involved_type']](involvement).data
            for involvement in obj.get('involvements', [])
        ]
