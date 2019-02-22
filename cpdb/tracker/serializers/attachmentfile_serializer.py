from rest_framework import serializers

from data.models import AttachmentFile


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
            'views_count',
            'downloads_count',
            'show',
            'documents_count'
        )
