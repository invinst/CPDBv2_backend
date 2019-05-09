from rest_framework import serializers

from data.models import AttachmentFile
from pinboard.serializers.allegation_card_serializer import AllegationCardSerializer


class DocumentCardSerializer(serializers.ModelSerializer):
    allegation = AllegationCardSerializer()

    class Meta:
        model = AttachmentFile
        fields = (
            'id',
            'preview_image_url',
            'url',
            'allegation',
        )
