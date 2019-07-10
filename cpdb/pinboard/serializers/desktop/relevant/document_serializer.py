from rest_framework import serializers

from data.models import AttachmentFile
from shared.serializer import NoNullSerializer
from ..common import OfficerRowSerializer


class AllegationSerializer(NoNullSerializer):
    crid = serializers.CharField()
    category = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    coaccused = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()

    def get_coaccused(self, obj):
        coaccused = [officer_allegation.officer for officer_allegation in obj.prefetched_officer_allegations]
        return OfficerRowSerializer(coaccused, many=True).data

    def get_category(self, obj):
        try:
            return obj.most_common_category.category
        except AttributeError:
            return 'Unknown'

    def get_point(self, obj):
        if obj.point is not None:
            return {'lon': obj.point.x, 'lat': obj.point.y}


class DocumentSerializer(serializers.ModelSerializer):
    allegation = AllegationSerializer()

    class Meta:
        model = AttachmentFile
        fields = (
            'id',
            'preview_image_url',
            'url',
            'allegation',
        )
