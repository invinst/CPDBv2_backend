from rest_framework import serializers
from data.models import AttachmentRequest


class CoaccusedSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='officer.id')
    badge = serializers.CharField(source='officer.current_badge')
    full_name = serializers.CharField(source='officer.full_name')
    gender = serializers.CharField(source='officer.gender_display')
    race = serializers.CharField(source='officer.race')
    final_finding = serializers.CharField(source='final_finding_display')
    recc_outcome = serializers.CharField(source='recc_outcome_display')
    final_outcome = serializers.CharField(source='final_outcome_display')
    category = serializers.CharField()
    subcategory = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class ComplainantSerializer(serializers.Serializer):
    gender = serializers.CharField(source='gender_display')
    race = serializers.CharField()
    age = serializers.IntegerField()


class InvolvementOfficerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    abbr_name = serializers.CharField()
    extra_info = serializers.SerializerMethodField()

    def get_extra_info(self, obj):
        return 'Badge %s' % obj.current_badge


class BeatSerializer(serializers.Serializer):
    name = serializers.CharField()


class AttachmentFileSerializer(serializers.Serializer):
    title = serializers.CharField()
    url = serializers.CharField()
    preview_image_url = serializers.CharField()


class CRSerializer(serializers.Serializer):
    crid = serializers.CharField()
    coaccused = CoaccusedSerializer(source='officer_allegations', many=True)
    complainants = ComplainantSerializer(many=True)
    point = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    address = serializers.CharField()
    location = serializers.SerializerMethodField()
    beat = BeatSerializer()
    involvements = serializers.SerializerMethodField()
    audios = AttachmentFileSerializer(many=True)
    videos = AttachmentFileSerializer(many=True)
    documents = AttachmentFileSerializer(many=True)

    def get_point(self, obj):
        if obj.point is not None:
            return {'long': obj.point.x, 'lat': obj.point.y}
        else:
            return None

    def get_location(self, obj):
        return obj.get_location_display()

    def get_involvements(self, obj):
        results = dict()
        for involvement in obj.involvement_set.filter(officer__isnull=False):
            results.setdefault(involvement.involved_type, list()).append(
                InvolvementOfficerSerializer(involvement.officer).data)
        results = [
            {'involved_type': involved_type, 'officers': officers}
            for involved_type, officers in results.iteritems()]
        return results


class AttachmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachmentRequest
        fields = '__all__'


class AllegationWithNewDocumentsSerializer(serializers.Serializer):
    crid = serializers.CharField()
    latest_document = AttachmentFileSerializer(source='get_latest_document')
    num_recent_documents = serializers.IntegerField()
