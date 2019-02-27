from threading import Thread

from rest_framework import serializers

from data.models import AttachmentFile
from data.constants import AttachmentSourceType



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
    last_updated_by = serializers.CharField(source='last_updated_by.username', allow_null=True)
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
        manually_updated_fields = ['text_content', 'title']
        updated_to_documentcloud_fields = ['title']

        for field in manually_updated_fields:
            value = getattr(self.instance, field, '')
            new_value = self.validated_data[field]
            if value != new_value:
                self.validated_data['manually_updated'] = True
                if field in updated_to_documentcloud_fields:
                    # TODO: we need to setup background task or kubernetes job for this
                    Thread(target=lambda: self.instance.update_to_documentcloud(field, new_value)).start()

        super(UpdateAttachmentFileSerializer, self).save()
