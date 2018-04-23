from datetime import datetime

from rest_framework import serializers


class CoaccusedSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='officer.id')
    full_name = serializers.CharField(source='officer.full_name')
    gender = serializers.CharField(source='officer.gender_display')
    race = serializers.CharField(source='officer.race')
    rank = serializers.CharField(source='officer.rank')
    final_outcome = serializers.CharField(source='final_outcome_display')
    final_finding = serializers.CharField(source='final_finding_display')
    recc_outcome = serializers.CharField(source='recc_outcome_display')
    category = serializers.CharField()
    subcategory = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    age = serializers.IntegerField(source='officer.current_age')
    allegation_count = serializers.IntegerField(source='officer.allegation_count')
    sustained_count = serializers.IntegerField(source='officer.sustained_count')


class ComplainantSerializer(serializers.Serializer):
    gender = serializers.CharField(source='gender_display')
    race = serializers.CharField()
    age = serializers.IntegerField()


class VictimSerializer(serializers.Serializer):
    gender = serializers.CharField(source='gender_display')
    race = serializers.CharField()
    age = serializers.IntegerField()


class AttachmentFileSerializer(serializers.Serializer):
    title = serializers.CharField()
    url = serializers.CharField()
    preview_image_url = serializers.CharField()
    file_type = serializers.CharField()


class InvestigatorAllegationSerializer(serializers.Serializer):
    officer_id = serializers.IntegerField(source='investigator.officer.id')
    involved_type = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    abbr_name = serializers.SerializerMethodField()
    num_cases = serializers.IntegerField(source='investigator.num_cases')
    current_rank = serializers.CharField()

    def get_involved_type(self, obj):
        return 'investigator'

    def get_full_name(self, obj):
        return getattr(obj.investigator.officer, 'full_name', obj.investigator.full_name)

    def get_abbr_name(self, obj):
        return getattr(obj.investigator.officer, 'abbr_name', obj.investigator.abbr_name)


class PoliceWitnessSerializer(serializers.Serializer):
    officer_id = serializers.IntegerField(source='officer.id')
    involved_type = serializers.SerializerMethodField()
    full_name = serializers.CharField(source='officer.full_name')
    abbr_name = serializers.CharField(source='officer.abbr_name')
    allegation_count = serializers.IntegerField(source='officer.allegation_count')
    sustained_count = serializers.IntegerField(source='officer.sustained_count')
    gender = serializers.CharField(source='officer.gender_display')
    race = serializers.CharField(source='officer.race')

    def get_involved_type(self, obj):
        return 'police_witness'


class CRDocSerializer(serializers.Serializer):
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
    attachments = AttachmentFileSerializer(source='attachment_files', many=True)

    def get_point(self, obj):
        if obj.point is not None:
            return {'lon': obj.point.x, 'lat': obj.point.y}
        else:
            return None

    def get_location(self, obj):
        return obj.get_location_display()

    def get_involvements(self, obj):
        return (
            InvestigatorAllegationSerializer(obj.investigatorallegation_set.all(), many=True).data +
            PoliceWitnessSerializer(obj.policewitness_set.all(), many=True).data
        )

    def get_beat(self, obj):
        return obj.beat.name if obj.beat is not None else None
