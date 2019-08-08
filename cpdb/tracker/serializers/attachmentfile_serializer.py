from rest_framework import serializers

from data.models import AttachmentFile
from data.constants import AttachmentSourceType


class AttachmentFileListSerializer(serializers.ModelSerializer):
    crid = serializers.CharField(source='allegation_id')
    documents_count = serializers.IntegerField()

    class Meta:
        model = AttachmentFile
        fields = (
            'id',
            'created_at',
            'crid',
            'title',
            'source_type',
            'preview_image_url',
            'show',
            'documents_count',
            'show',
            'file_type',
            'url',
        )


class AuthenticatedAttachmentFileListSerializer(serializers.ModelSerializer):
    crid = serializers.CharField(source='allegation_id')
    documents_count = serializers.IntegerField()

    class Meta(AttachmentFileListSerializer.Meta):
        fields = AttachmentFileListSerializer.Meta.fields + (
            'views_count',
            'downloads_count'
        )


crawler_name_map = {
    AttachmentSourceType.PORTAL_COPA: 'Chicago COPA',
    AttachmentSourceType.SUMMARY_REPORTS_COPA: 'Chicago COPA',
    AttachmentSourceType.DOCUMENTCLOUD: 'Document Cloud',
    AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD: 'Chicago COPA',
    AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD: 'Chicago COPA',
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
            'notifications_count',
            'tags',
        )


class UpdateAttachmentFileSerializer(serializers.ModelSerializer):
    def __init__(self, user, **kwargs):
        self.user = user
        super(UpdateAttachmentFileSerializer, self).__init__(**kwargs)

    class Meta:
        model = AttachmentFile
        fields = ('show', 'title', 'text_content', 'last_updated_by', 'tags')

    def save(self):
        manually_updated_fields = ['text_content', 'title', 'tags']

        changed = False
        for field in manually_updated_fields:
            if field in self.validated_data:
                value = getattr(self.instance, field, None)
                new_value = self.validated_data[field]
                if value != new_value:
                    changed = True

        if changed:
            self.validated_data['manually_updated'] = True
            self.validated_data['last_updated_by_id'] = self.user.id
        super(UpdateAttachmentFileSerializer, self).save()

    def is_valid(self, raise_exception=True):
        needed_fields = ('show', 'title', 'text_content', 'tags')
        if all(key not in self.initial_data for key in needed_fields):
            return False
        return super(UpdateAttachmentFileSerializer, self).is_valid(raise_exception)
