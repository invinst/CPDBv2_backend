from rest_framework import serializers

from data.constants import GENDER_DICT
from data.models import Officer, PoliceUnit
from shared.serializer import OfficerPercentileSerializer
from shared.serializer import NoNullSerializer
from trr.models import TRRAttachmentRequest


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliceUnit
        fields = ['unit_name', 'description']


class OfficerSerializer(OfficerPercentileSerializer, serializers.ModelSerializer):
    gender = serializers.CharField(source='gender_display', read_only=True)
    unit = UnitSerializer(source='last_unit', allow_null=True, read_only=True)

    class Meta:
        model = Officer
        fields = [
            'id', 'full_name', 'race', 'appointed_date', 'birth_year',
            'resignation_date', 'unit', 'gender', 'rank',
            'percentile_allegation', 'percentile_allegation_civilian',
            'percentile_allegation_internal', 'percentile_trr'
        ]


class TRRSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    officer = OfficerSerializer()
    officer_in_uniform = serializers.BooleanField(default=False)
    officer_assigned_beat = serializers.CharField(max_length=16, allow_null=True)
    officer_on_duty = serializers.BooleanField(default=False)

    subject_race = serializers.CharField(max_length=32)
    subject_gender = serializers.SerializerMethodField()
    subject_age = serializers.IntegerField()
    force_category = serializers.CharField(max_length=255)
    force_types = serializers.ListField(child=serializers.CharField(max_length=255))
    actions = serializers.ListField(child=serializers.CharField(max_length=255))

    date_of_incident = serializers.SerializerMethodField()
    location_type = serializers.CharField(source='location_recode')
    address = serializers.SerializerMethodField()
    beat = serializers.IntegerField()
    point = serializers.SerializerMethodField()

    def get_subject_gender(self, obj):
        try:
            return GENDER_DICT[obj.subject_gender]
        except KeyError:
            return obj.subject_gender

    def get_address(self, obj):
        return ' '.join(filter(None, [obj.block, obj.street]))

    def get_date_of_incident(self, obj):
        return obj.trr_datetime.date().strftime('%Y-%m-%d')

    def get_point(self, obj):
        if obj.point is not None:
            return {'lng': obj.point.x, 'lat': obj.point.y}
        else:
            return None


class AttachmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TRRAttachmentRequest
        fields = '__all__'
