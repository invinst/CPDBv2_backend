from rest_framework import serializers

from shared.serializer import NoNullSerializer
from social_graph.serializers.cr_detail_serializer import CRDetailSerializer


class AttachmentFileSerializer(NoNullSerializer):
    title = serializers.CharField()
    url = serializers.CharField()
    preview_image_url = serializers.CharField()
    file_type = serializers.CharField()
    id = serializers.CharField()


class SocialGraphCRDetailSerializer(CRDetailSerializer):
    attachments = AttachmentFileSerializer(source='prefetch_filtered_attachment_files', many=True)
    officer_ids = serializers.SerializerMethodField()

    def get_officer_ids(self, obj):
        return [officer_allegation.officer_id for officer_allegation in obj.officer_allegations]
