from rest_framework import serializers

from data.models import AttachmentFile


class AttachmentFileListSerializer(serializers.ModelSerializer):
    crid = serializers.CharField(source='allegation_id')

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
            'show'
        )
