from rest_framework import serializers

from data.models import AttachmentFile
from data.constants import AttachmentSourceType, MEDIA_TYPE_DOCUMENT


class AttachmentFileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachmentFile
        fields = (
            'id',
            'created_at',
            'title',
            'source_type',
            'preview_image_url',
            'views_count',
            'downloads_count',
            'show',
        )


crawler_name_map = {
    AttachmentSourceType.DOCUMENTCLOUD: 'Document Cloud',
    AttachmentSourceType.COPA_DOCUMENTCLOUD: 'Chicago COPA',
}


class LinkedAttachmentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachmentFile
        fields = ('id', 'preview_image_url')


class AttachmentFileSerializer(serializers.ModelSerializer):
    crid = serializers.CharField(source='allegation_id')
    crawler_name = serializers.SerializerMethodField()
    linked_documents = LinkedAttachmentFileSerializer(many=True)

    def get_crawler_name(self, obj):
        return crawler_name_map.get(obj.source_type, 'Unknown')

    class Meta:
        model = AttachmentFile
        fields = (
            'id',
            'crid',
            'title',
            'text_content',
            'url',
            'preview_image_url',
            'original_url',
            'created_at',
            'updated_at',
            'crawler_name',
            'linked_documents',
            'pages'
        )


class AuthenticatedAttachmentFileSerializer(AttachmentFileSerializer):
    class Meta(AttachmentFileSerializer.Meta):
        fields = AttachmentFileSerializer.Meta.fields + (
            'views_count',
            'downloads_count',
            'notifications_count'
        )
