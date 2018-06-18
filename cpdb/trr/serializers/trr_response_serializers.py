from rest_framework import serializers


class UnitSerializer(serializers.Serializer):
    unit_name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=255, allow_null=True)


class OfficerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField(max_length=255)
    gender = serializers.CharField(max_length=255)
    race = serializers.CharField(max_length=50)
    appointed_date = serializers.DateField(allow_null=True)
    birth_year = serializers.IntegerField(allow_null=True)
    resignation_date = serializers.DateField(read_only=True, allow_null=True)
    unit = UnitSerializer(source='last_unit')
    percentile_allegation_civilian = serializers.FloatField(allow_null=True)
    percentile_allegation_internal = serializers.FloatField(allow_null=True)
    percentile_trr = serializers.FloatField(allow_null=True)


class TRRDesktopSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    officer = OfficerSerializer(read_only=True)
    officer_in_uniform = serializers.BooleanField(default=False)
    officer_assigned_beat = serializers.CharField(max_length=16, allow_null=True)
    officer_on_duty = serializers.BooleanField(default=False)
