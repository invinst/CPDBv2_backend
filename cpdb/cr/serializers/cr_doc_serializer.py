from rest_framework import serializers


class CoaccusedSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='officer.id')
    full_name = serializers.CharField(source='officer.full_name')
    abbr_name = serializers.CharField(source='officer.abbr_name')
    gender = serializers.CharField(source='officer.gender_display')
    race = serializers.CharField(source='officer.race')
    rank = serializers.CharField(source='officer.rank')
    final_outcome = serializers.CharField()
    final_finding = serializers.CharField(source='final_finding_display')
    recc_outcome = serializers.CharField()
    category = serializers.CharField()
    subcategory = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    age = serializers.IntegerField(source='officer.current_age')
    allegation_count = serializers.IntegerField(source='officer.allegation_count')
    sustained_count = serializers.IntegerField(source='officer.sustained_count')
    disciplined = serializers.NullBooleanField()

    percentile_allegation = serializers.FloatField(source='officer.complaint_percentile')
    percentile_allegation_civilian = serializers.FloatField(source='officer.civilian_allegation_percentile')
    percentile_allegation_internal = serializers.FloatField(source='officer.internal_allegation_percentile')
    percentile_trr = serializers.FloatField(source='officer.trr_percentile')


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

    percentile_allegation = serializers.FloatField(
        source='investigator.officer.complaint_percentile')
    percentile_allegation_civilian = serializers.FloatField(
        source='investigator.officer.civilian_allegation_percentile')
    percentile_allegation_internal = serializers.FloatField(
        source='investigator.officer.internal_allegation_percentile')
    percentile_trr = serializers.FloatField(
        source='investigator.officer.trr_percentile')

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

    percentile_allegation = serializers.FloatField(source='officer.complaint_percentile')
    percentile_allegation_civilian = serializers.FloatField(source='officer.civilian_allegation_percentile')
    percentile_allegation_internal = serializers.FloatField(source='officer.internal_allegation_percentile')
    percentile_trr = serializers.FloatField(source='officer.trr_percentile')

    def get_involved_type(self, obj):
        return 'police_witness'


class AllegationCategorySerializer(serializers.Serializer):
    category = serializers.CharField()
    allegation_name = serializers.CharField()


class CRDocSerializer(serializers.Serializer):
    crid = serializers.CharField()
    category_names = serializers.ListField(child=serializers.CharField())
    most_common_category = AllegationCategorySerializer(source='get_most_common_category')
    coaccused = CoaccusedSerializer(source='officer_allegations', many=True)
    complainants = ComplainantSerializer(many=True)
    victims = VictimSerializer(many=True)
    summary = serializers.CharField()
    point = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    start_date = serializers.DateTimeField(source='first_start_date', format='%Y-%m-%d')
    end_date = serializers.DateTimeField(source='first_end_date', format='%Y-%m-%d')
    address = serializers.CharField()
    location = serializers.CharField()
    beat = serializers.SerializerMethodField()
    involvements = serializers.SerializerMethodField()
    attachments = AttachmentFileSerializer(source='attachment_files', many=True)

    def get_point(self, obj):
        if obj.point is not None:
            return {'lon': obj.point.x, 'lat': obj.point.y}
        else:
            return None

    def get_involvements(self, obj):
        return (
            InvestigatorAllegationSerializer(obj.investigatorallegation_set.all(), many=True).data +
            PoliceWitnessSerializer(obj.policewitness_set.all(), many=True).data
        )

    def get_beat(self, obj):
        return obj.beat.name if obj.beat is not None else None
