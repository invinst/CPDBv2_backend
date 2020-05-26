from rest_framework import serializers
from django.db.models import Prefetch, Exists, OuterRef

import pytz

from data.models import AttachmentRequest, Investigator
from shared.serializer import NoNullSerializer, OfficerPercentileSerializer


class CoaccusedSerializer(NoNullSerializer):
    id = serializers.IntegerField(source='officer.id')
    full_name = serializers.CharField(source='officer.full_name')
    complaint_count = serializers.IntegerField(source='officer.allegation_count')
    sustained_count = serializers.IntegerField(source='officer.sustained_count')
    birth_year = serializers.IntegerField(source='officer.birth_year')
    recommended_outcome = serializers.CharField(source='recc_outcome')
    final_outcome = serializers.CharField()
    final_finding = serializers.CharField(source='final_finding_display')
    category = serializers.CharField()
    disciplined = serializers.NullBooleanField()
    race = serializers.CharField(source='officer.race')
    gender = serializers.CharField(source='officer.gender_display')
    rank = serializers.CharField(source='officer.rank')

    percentile_allegation = serializers.DecimalField(
        source='officer.complaint_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4
    )
    percentile_trr = serializers.DecimalField(
        source='officer.trr_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4
    )
    percentile_allegation_civilian = serializers.DecimalField(
        source='officer.civilian_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4
    )
    percentile_allegation_internal = serializers.DecimalField(
        source='officer.internal_allegation_percentile', allow_null=True, read_only=True, max_digits=6, decimal_places=4
    )


class ComplainantSerializer(NoNullSerializer):
    gender = serializers.CharField(source='gender_display')
    race = serializers.CharField()
    age = serializers.IntegerField()


class VictimSerializer(NoNullSerializer):
    gender = serializers.CharField(source='gender_display')
    race = serializers.CharField()
    age = serializers.IntegerField()


class AttachmentFileSerializer(NoNullSerializer):
    title = serializers.CharField()
    url = serializers.CharField()
    preview_image_url = serializers.CharField()
    file_type = serializers.CharField()
    id = serializers.CharField()


class InvestigatorAllegationSerializer(NoNullSerializer):
    officer_id = serializers.IntegerField(required=False, source='investigator.officer.id')
    involved_type = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    badge = serializers.SerializerMethodField()

    percentile_allegation = serializers.DecimalField(
        source='investigator.officer.complaint_percentile', max_digits=6, decimal_places=4, allow_null=True)
    percentile_allegation_civilian = serializers.DecimalField(
        source='investigator.officer.civilian_allegation_percentile', max_digits=6, decimal_places=4, allow_null=True)
    percentile_allegation_internal = serializers.DecimalField(
        source='investigator.officer.internal_allegation_percentile', max_digits=6, decimal_places=4, allow_null=True)
    percentile_trr = serializers.DecimalField(
        source='investigator.officer.trr_percentile', max_digits=6, decimal_places=4, allow_null=True)

    def get_involved_type(self, obj):
        return 'investigator'

    def get_full_name(self, obj):
        return getattr(obj.investigator.officer, 'full_name', obj.investigator.full_name)

    def get_badge(self, obj):
        incident_date = obj.allegation.incident_date

        pre_2006 = incident_date and incident_date.year < 2006
        if pre_2006 or obj.current_star or obj.has_badge_number:
            return 'CPD'
        else:
            return 'COPA/IPRA'


class PoliceWitnessSerializer(OfficerPercentileSerializer):
    officer_id = serializers.IntegerField(source='id')
    involved_type = serializers.SerializerMethodField()
    full_name = serializers.CharField()
    allegation_count = serializers.IntegerField()
    sustained_count = serializers.IntegerField()

    def get_involved_type(self, obj):
        return 'police_witness'


class AllegationCategorySerializer(NoNullSerializer):
    category = serializers.CharField()
    allegation_name = serializers.CharField()


class CRSerializer(NoNullSerializer):
    crid = serializers.CharField()
    most_common_category = AllegationCategorySerializer()
    coaccused = serializers.SerializerMethodField()
    complainants = ComplainantSerializer(many=True)
    victims = VictimSerializer(many=True)
    summary = serializers.CharField()
    point = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)
    start_date = serializers.DateField(source='first_start_date', format='%Y-%m-%d')
    end_date = serializers.DateField(source='first_end_date', format='%Y-%m-%d')
    address = serializers.CharField()
    location = serializers.CharField()
    beat = serializers.SerializerMethodField()
    involvements = serializers.SerializerMethodField()
    attachments = AttachmentFileSerializer(source='filtered_attachment_files', many=True)

    def get_coaccused(self, obj):
        officer_allegations = obj.officer_allegations.select_related(
            'allegation_category'
        ).prefetch_related('officer')

        return CoaccusedSerializer(officer_allegations, many=True).data

    def get_point(self, obj):
        if obj.point is not None:
            return {'lon': obj.point.x, 'lat': obj.point.y}
        else:
            return None

    def get_involvements(self, obj):
        return (
            InvestigatorAllegationSerializer(self.get_investigator_allegation(obj), many=True).data +
            PoliceWitnessSerializer(obj.police_witnesses.all(), many=True).data
        )

    def get_investigator_allegation(self, obj):
        return obj.investigatorallegation_set\
            .prefetch_related(Prefetch('investigator__officer'))\
            .annotate(
                has_badge_number=Exists(
                    Investigator.objects.filter(
                        id=OuterRef('investigator_id'),
                        officer__officerbadgenumber__isnull=False
                    )
                )
            )

    def get_beat(self, obj):
        return obj.beat.name if obj.beat is not None else None


class CRSummarySerializer(NoNullSerializer):
    crid = serializers.CharField()
    category_names = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)
    summary = serializers.CharField()

    def get_category_names(self, obj):
        if obj.categories:
            return sorted(category if category is not None else 'Unknown' for category in set(obj.categories))
        else:
            return ['Unknown']


class AttachmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachmentRequest
        fields = '__all__'


class AllegationWithNewDocumentsSerializer(NoNullSerializer):
    crid = serializers.CharField(source='allegation_id')
    latest_document = serializers.SerializerMethodField()
    category = serializers.CharField(source='allegation.most_common_category.category', allow_null=True)
    incident_date = serializers.DateTimeField(
        source='allegation.incident_date', format='%Y-%m-%d', default_timezone=pytz.utc
    )

    def get_latest_document(self, obj):
        return AttachmentFileSerializer(obj).data


class CRRelatedComplaintSerializer(NoNullSerializer):
    crid = serializers.CharField()
    complainants = serializers.SerializerMethodField()
    coaccused = serializers.SerializerMethodField()
    category_names = serializers.ListField(child=serializers.CharField())
    point = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)

    def get_coaccused(self, obj):
        try:
            return [coaccused.abbr_name for coaccused in obj.coaccused]
        except AttributeError:  # pragma: no cover
            return []

    def get_complainants(self, obj):
        try:
            return [complainant.to_dict() for complainant in obj.complainants]
        except AttributeError:
            return []

    def get_point(self, obj):
        try:
            return obj.point.to_dict()
        except AttributeError:  # pragma: no cover
            return None


class CRRelatedComplaintRequestSerializer(NoNullSerializer):
    match = serializers.ChoiceField(choices=['categories', 'officers'], required=True)
    distance = serializers.ChoiceField(choices=['0.5mi', '1mi', '2.5mi', '5mi', '10mi'], required=True)
    offset = serializers.IntegerField(default=0)
    limit = serializers.IntegerField(default=20)
