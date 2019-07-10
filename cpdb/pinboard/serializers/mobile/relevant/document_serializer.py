from rest_framework import serializers

from data.models import AttachmentFile
from .allegation_serializer import AllegationMobileSerializer


class DocumentSerializer(serializers.ModelSerializer):
    allegation = AllegationMobileSerializer()

    class Meta:
        model = AttachmentFile
        fields = (
            'id',
            'preview_image_url',
            'url',
            'allegation',
        )
