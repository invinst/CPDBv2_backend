from datetime import datetime

from rest_framework import serializers

from data.models import AttachmentRequest


class CoaccusedSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='officer.id')
    full_name = serializers.CharField(source='officer.full_name')
    gender = serializers.CharField(source='officer.gender_display')
    race = serializers.CharField(source='officer.race')
    final_outcome = serializers.CharField(source='final_outcome_display')
    category = serializers.CharField()
    age = serializers.SerializerMethodField()
    allegation_count = serializers.IntegerField(source='officer.allegation_count')
    sustained_count = serializers.IntegerField(source='officer.sustained_count')

    def get_age(self, obj):
        return datetime.now().year - obj.officer.birth_year


class ComplainantSerializer(serializers.Serializer):
    gender = serializers.CharField(source='gender_display')
    race = serializers.CharField()
    age = serializers.IntegerField()


class VictimSerializer(serializers.Serializer):
    gender = serializers.CharField(source='gender_display')
    race = serializers.CharField()
    age = serializers.IntegerField()


class InvolvementOfficerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    abbr_name = serializers.CharField()
    extra_info = serializers.SerializerMethodField()

    def get_extra_info(self, obj):
        return 'Badge %s' % obj.current_badge


class AttachmentFileSerializer(serializers.Serializer):
    title = serializers.CharField()
    url = serializers.CharField()
    preview_image_url = serializers.CharField()
    file_type = serializers.CharField()


class CRSerializer(serializers.Serializer):
    crid = serializers.CharField()
    category_names = serializers.ListField(child=serializers.CharField())
    coaccused = CoaccusedSerializer(source='officer_allegations', many=True)
    complainants = ComplainantSerializer(many=True)
    victims = VictimSerializer(many=True)
    summary = serializers.CharField()
    point = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    start_date = serializers.DateTimeField(source='first_start_date', format='%Y-%m-%d')
    end_date = serializers.DateTimeField(source='first_end_date', format='%Y-%m-%d')
    address = serializers.CharField()
    location = serializers.SerializerMethodField()
    beat = serializers.SerializerMethodField()
    involvements = serializers.SerializerMethodField()
    attachments = AttachmentFileSerializer(source='documents', many=True)

    def get_point(self, obj):
        if obj.point is not None:
            return {'lon': obj.point.x, 'lat': obj.point.y}
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

    def get_beat(self, obj):
        return obj.beat.name if obj.beat is not None else None


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
    latest_document = AttachmentFileSerializer(source='get_newest_added_document')
    num_recent_documents = serializers.IntegerField()
