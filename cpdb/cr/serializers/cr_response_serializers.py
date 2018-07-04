from rest_framework import serializers

from .base import CherryPickSerializer
from data.models import AttachmentRequest


class CoaccusedDesktopSerializer(CherryPickSerializer):
    class Meta(object):
        fields = (
            'id',
            'full_name',
            'gender',
            'race',
            'rank',
            'age',
            'allegation_count',
            'sustained_count',
            'final_outcome',
            'final_finding',
            'category',
            'percentile_allegation',
            'percentile_allegation_civilian',
            'percentile_allegation_internal',
            'percentile_trr'
        )


class InvestigatorSerializer(CherryPickSerializer):
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


class PoliceWitnessSerializer(CherryPickSerializer):
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


class CRDesktopSerializer(serializers.Serializer):
    crid = serializers.CharField()
    most_common_category = serializers.JSONField(required=False)
    coaccused = CoaccusedDesktopSerializer(many=True, default=[])
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
            'investigator': InvestigatorSerializer,
            'police_witness': PoliceWitnessSerializer
        }
        return [
            serializer_map[involvement['involved_type']](involvement).data
            for involvement in obj.get('involvements', [])
        ]


class CoaccusedMobileSerializer(CherryPickSerializer):
    class Meta(object):
        fields = (
            'id',
            'full_name',
            'rank',
            'final_outcome',
            'final_finding',
            'category',
            'percentile_allegation',
            'percentile_allegation_civilian',
            'percentile_allegation_internal',
            'percentile_trr'
        )


class AttachmentField(serializers.Field):
    def __init__(self, type, *args, **kwargs):
        super(AttachmentField, self).__init__(*args, **kwargs)
        self.type = type

    def to_representation(self, obj):
        return [
            {
                'title': attachment['title'],
                'url': attachment['url']
            } for attachment in obj if attachment['file_type'] == self.type
        ]


class CRMobileSerializer(serializers.Serializer):
    crid = serializers.CharField()
    most_common_category = serializers.JSONField(required=False)
    coaccused = CoaccusedMobileSerializer(many=True)
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
            'investigator': InvestigatorSerializer,
            'police_witness': PoliceWitnessSerializer
        }
        return [
            serializer_map[involvement['involved_type']](involvement).data
            for involvement in obj.get('involvements', [])
        ]


class LatestDocumentSerializer(serializers.Serializer):
    title = serializers.CharField()
    url = serializers.CharField()
    preview_image_url = serializers.CharField()


class CRSummarySerializer(serializers.Serializer):
    crid = serializers.CharField()
    category_names = serializers.ListField(child=serializers.CharField())
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    summary = serializers.CharField()


class AttachmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachmentRequest
        fields = '__all__'


class AttachmentFileSerializer(serializers.Serializer):
    title = serializers.CharField()
    url = serializers.CharField()
    preview_image_url = serializers.CharField()


class AllegationWithNewDocumentsSerializer(serializers.Serializer):
    crid = serializers.CharField()
    latest_document = serializers.SerializerMethodField()
    num_recent_documents = serializers.SerializerMethodField()

    def get_latest_document(self, obj):
        return AttachmentFileSerializer(obj.latest_documents[-1]).data if obj.latest_documents else None

    def get_num_recent_documents(self, obj):
        return len(obj.latest_documents)


class CRRelatedComplaintRequestSerializer(serializers.Serializer):
    match = serializers.ChoiceField(choices=['categories', 'officers'], required=True)
    distance = serializers.ChoiceField(choices=['0.5mi', '1mi', '2.5mi', '5mi', '10mi'], required=True)
    offset = serializers.IntegerField(default=0)
    limit = serializers.IntegerField(default=20)


class CRRelatedComplaintSerializer(serializers.Serializer):
    crid = serializers.CharField()
    complainants = serializers.SerializerMethodField()
    coaccused = serializers.SerializerMethodField()
    category_names = serializers.ListField(child=serializers.CharField())
    point = serializers.SerializerMethodField()

    def get_coaccused(self, obj):
        try:
            return [coaccused.abbr_name for coaccused in obj.coaccused]
        except AttributeError:
            return []

    def get_complainants(self, obj):
        try:
            return [complainant.to_dict() for complainant in obj.complainants]
        except AttributeError:
            return []

    def get_point(self, obj):
        try:
            return obj.point.to_dict()
        except AttributeError:  # pragma: no cover
            return None
