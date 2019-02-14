from rest_framework import serializers

from data.models import AttachmentFile


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
            'show'
        )
