from rest_framework import serializers

from data.models import PoliceUnit
from shared.serializer import OfficerPercentileSerializer


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliceUnit
        fields = ['id', 'unit_name', 'description']


class OfficerDetailSerializer(OfficerPercentileSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    rank = serializers.CharField()
    badge = serializers.CharField(source='current_badge')
    race = serializers.CharField()
    birth_year = serializers.CharField()
    unit = UnitSerializer(source='last_unit', allow_null=True, read_only=True)
    gender = serializers.CharField()
    allegation_count = serializers.IntegerField()
    sustained_count = serializers.IntegerField()
    honorable_mention_count = serializers.IntegerField()
    major_award_count = serializers.IntegerField()
    trr_count = serializers.IntegerField()
    discipline_count = serializers.IntegerField()
    civilian_compliment_count = serializers.IntegerField()
    resignation_date = serializers.DateField(format='%Y-%m-%d')
    appointed_date = serializers.DateField(format='%Y-%m-%d')
    honorable_mention_percentile = serializers.DecimalField(
        read_only=True, max_digits=6, decimal_places=4, allow_null=True
    )
