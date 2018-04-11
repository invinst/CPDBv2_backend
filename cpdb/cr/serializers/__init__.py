from rest_framework import serializers

from data.models import AttachmentRequest


class LatestDocumentSerializer(serializers.Serializer):
    title = serializers.CharField()
    url = serializers.CharField()
    preview_image_url = serializers.CharField()


class CRSummarySerializer(serializers.Serializer):
    crid = serializers.CharField()
    category_names = serializers.ListField(child=serializers.CharField())
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    summary = serializers.CharField()


class AttachmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachmentRequest
        fields = '__all__'


class AllegationWithNewDocumentsSerializer(serializers.Serializer):
    crid = serializers.CharField()
    latest_document = LatestDocumentSerializer(source='get_newest_added_document')
    num_recent_documents = serializers.IntegerField()
