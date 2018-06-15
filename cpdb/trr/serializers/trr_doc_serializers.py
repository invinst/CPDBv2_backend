from rest_framework import serializers

from data.models import Officer, PoliceUnit


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliceUnit
        fields = ['unit_name', 'description']


class OfficerSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(source='gender_display', read_only=True)
    last_unit = UnitSerializer(allow_null=True, read_only=True)

    class Meta:
        model = Officer
        fields = [
            'id', 'full_name', 'race', 'appointed_date', 'birth_year',
            'resignation_date', 'last_unit', 'gender'
        ]


class TRRDocSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    officer = OfficerSerializer()
    officer_in_uniform = serializers.BooleanField(default=False)
    officer_assigned_beat = serializers.CharField(max_length=16, allow_null=True)
    officer_on_duty = serializers.BooleanField(default=False)
