from rest_framework import serializers

from data.models import Officer
from shared.serializer import NoNullSerializer, OfficerPercentileSerializer


class OfficerRowSerializer(serializers.ModelSerializer):
    coaccusal_count = serializers.IntegerField(allow_null=True)
    allegation_count = serializers.IntegerField()
    percentile = serializers.SerializerMethodField()

    def get_percentile(self, obj):
        return OfficerPercentileSerializer(obj).data

    class Meta:
        model = Officer
        fields = (
            'id',
            'rank',
            'full_name',
            'coaccusal_count',
            'percentile',
            'allegation_count',
        )


class OfficerSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    date_of_appt = serializers.DateField(source='appointed_date', format='%Y-%m-%d')
    date_of_resignation = serializers.DateField(source='resignation_date', format='%Y-%m-%d')
    badge = serializers.SerializerMethodField()
    gender = serializers.CharField(source='gender_display')
    to = serializers.CharField(source='v2_to')
    birth_year = serializers.IntegerField()
    race = serializers.CharField()
    rank = serializers.CharField()
    percentile = serializers.SerializerMethodField()
    allegation_count = serializers.IntegerField()
    civilian_compliment_count = serializers.IntegerField()
    sustained_count = serializers.IntegerField()
    discipline_count = serializers.IntegerField()
    trr_count = serializers.IntegerField()
    major_award_count = serializers.IntegerField()
    honorable_mention_count = serializers.IntegerField()
    honorable_mention_percentile = serializers.FloatField(allow_null=True, read_only=True)

    def get_badge(self, obj):
        return obj.current_badge or ''

    def get_percentile(self, obj):
        return OfficerPercentileSerializer(obj).data
