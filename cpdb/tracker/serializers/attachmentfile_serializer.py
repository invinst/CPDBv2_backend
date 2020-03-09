from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer

from data.models import AttachmentFile
from data.constants import AttachmentSourceType
from tracker.constants import TAG_MAX_LENGTH
from data.constants import MEDIA_TYPE_DOCUMENT


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


class SortedTagListSerializerField(TagListSerializerField):
    order_by = ['name']


class AuthenticatedAttachmentFileSerializer(TaggitSerializer, AttachmentFileSerializer):
    next_document_id = serializers.SerializerMethodField()
    tags = SortedTagListSerializerField()

    def get_next_document_id(self, obj):
        next_attachment = AttachmentFile.objects.exclude(
            id=obj.id
        ).filter(
            file_type=MEDIA_TYPE_DOCUMENT,
            tags__isnull=True,
            created_at__lte=obj.created_at
        ).order_by('-created_at').first()

        if not next_attachment:
            next_attachment = AttachmentFile.objects.exclude(
                id=obj.id
            ).filter(
                file_type=MEDIA_TYPE_DOCUMENT,
                tags__isnull=True
            ).order_by('-created_at').first()

        return next_attachment.id if next_attachment else None

    class Meta(AttachmentFileSerializer.Meta):
        fields = AttachmentFileSerializer.Meta.fields + (
            'views_count',
            'downloads_count',
            'notifications_count',
            'tags',
            'next_document_id',
        )


class UpdateAttachmentFileSerializer(TaggitSerializer, serializers.ModelSerializer):
    def __init__(self, user, **kwargs):
        self.user = user
        super(UpdateAttachmentFileSerializer, self).__init__(**kwargs)

    tags = SortedTagListSerializerField(required=False)

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

    def validate_tags(self, tags):
        for tag in tags:
            if len(tag) > TAG_MAX_LENGTH:
                raise ValidationError(f'Ensure this field has no more than {TAG_MAX_LENGTH} characters.')
        return tags
