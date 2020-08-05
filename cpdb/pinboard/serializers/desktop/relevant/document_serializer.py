from rest_framework import serializers

from data.models import AttachmentFile
from .allegation_serializer import AllegationSerializer


class DocumentSerializer(serializers.ModelSerializer):
    allegation = AllegationSerializer(source='owner')

    class Meta:
        model = AttachmentFile
        fields = (
            'id',
            'preview_image_url',
            'url',
            'allegation',
        )
