from rest_framework import serializers

from trr.models import TRRAttachmentRequest
from shared.serializer import NoNullSerializer


class UnitSerializer(NoNullSerializer):
    unit_name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=255, allow_null=True)


class OfficerSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField(max_length=255)
    gender = serializers.CharField(max_length=255)
    race = serializers.CharField(max_length=50)
    rank = serializers.CharField(max_length=100)
    appointed_date = serializers.DateField(allow_null=True)
    birth_year = serializers.IntegerField(allow_null=True)
    resignation_date = serializers.DateField(read_only=True, allow_null=True)
    unit = UnitSerializer(required=False, source='last_unit')
    percentile_allegation_civilian = serializers.FloatField(required=False, allow_null=True)
    percentile_allegation_internal = serializers.FloatField(required=False, allow_null=True)
    percentile_trr = serializers.FloatField(required=False, allow_null=True)


class TRRSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    officer = OfficerSerializer(read_only=True)
    officer_in_uniform = serializers.BooleanField(read_only=True, default=False)
    officer_assigned_beat = serializers.CharField(read_only=True, max_length=16, allow_null=True)
    officer_on_duty = serializers.BooleanField(read_only=True, default=False)

    subject_race = serializers.CharField(read_only=True, max_length=32, allow_null=True)
    subject_gender = serializers.CharField(read_only=True, max_length=32, allow_null=True)
    subject_age = serializers.IntegerField(allow_null=True, read_only=True)
    force_category = serializers.CharField(max_length=255)
    force_types = serializers.ListField(read_only=True, child=serializers.CharField(max_length=255))

    date_of_incident = serializers.CharField(max_length=10)

    location_type = serializers.CharField(required=False, max_length=255)
    address = serializers.CharField(max_length=255, allow_null=True)
    beat = serializers.IntegerField(required=False, allow_null=True)
    point = serializers.DictField(read_only=True, child=serializers.FloatField())


class AttachmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TRRAttachmentRequest
        fields = '__all__'
