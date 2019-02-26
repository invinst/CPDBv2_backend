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
    last_updated_by = serializers.CharField(source='last_updated_by.username')
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
            'pages',
            'last_updated_by',
        )


class AuthenticatedAttachmentFileSerializer(AttachmentFileSerializer):
    class Meta(AttachmentFileSerializer.Meta):
        fields = AttachmentFileSerializer.Meta.fields + (
            'views_count',
            'downloads_count',
            'notifications_count'
        )


class UpdateAttachmentFileSerializer(serializers.ModelSerializer):
    def __init__(self, instance, data, **kwargs):
        super(UpdateAttachmentFileSerializer, self).__init__(instance, data, partial=True, **kwargs)

    class Meta:
        model = AttachmentFile
        fields = ('id', 'show', 'title', 'text_content', 'last_updated_by')
        read_only_fields = ('id',)

    def save(self):
        if self.instance.text_content != self.validated_data['text_content'] and not self.instance.manually_updated:
            self.validated_data['manually_updated'] = True
        super(UpdateAttachmentFileSerializer, self).save()
