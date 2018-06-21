from rest_framework import serializers


class TimelineSerializer(serializers.Serializer):
    def to_representation(self, obj):
        result = obj.to_dict()
        result.pop('officer_id')
        result.pop('date_sort')
        result.pop('year_sort')
        result.pop('priority_sort')
        return result


class NewTimelineSerializer(serializers.Serializer):
    def to_representation(self, obj):
        result = obj.to_dict()
        result.pop('officer_id')
        result.pop('date_sort')
        result.pop('priority_sort')
        return result


class OfficerYearlyPercentileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    year = serializers.IntegerField()
    percentile_trr = serializers.DecimalField(max_digits=6, decimal_places=3)
    percentile_allegation = serializers.DecimalField(max_digits=6, decimal_places=3)
    percentile_allegation_civilian = serializers.DecimalField(max_digits=6, decimal_places=3)
    percentile_allegation_internal = serializers.DecimalField(max_digits=6, decimal_places=3)


class PoliceUnitSerializer(serializers.Serializer):
    unit_id = serializers.IntegerField(source='id')
    unit_name = serializers.CharField(max_length=5)
    description = serializers.CharField(max_length=255)


class OfficerMobileSerializer(serializers.Serializer):
    officer_id = serializers.IntegerField(source='id')
    full_name = serializers.CharField(max_length=255)
    percentiles = OfficerYearlyPercentileSerializer(read_only=True, many=True, allow_null=True)
    unit = PoliceUnitSerializer(read_only=True, allow_null=True)
    date_of_appt = serializers.DateField(read_only=True, allow_null=True, format='%Y-%m-%d')
    date_of_resignation = serializers.DateField(read_only=True, allow_null=True, format='%Y-%m-%d')
    active = serializers.BooleanField()
    rank = serializers.CharField()
    race = serializers.CharField()
    birth_year = serializers.IntegerField(read_only=True, allow_null=True)
    badge = serializers.CharField(read_only=True, allow_null=True)
    historic_badges = serializers.ListField(read_only=True, allow_null=True, child=serializers.CharField())
    gender = serializers.CharField()
    allegation_count = serializers.IntegerField(read_only=True, allow_null=True)
    complaint_percentile = serializers.FloatField(read_only=True, allow_null=True)
    honorable_mention_count = serializers.IntegerField(read_only=True, allow_null=True)
    sustained_count = serializers.IntegerField(read_only=True, allow_null=True)
    discipline_count = serializers.IntegerField(read_only=True, allow_null=True)
    civilian_compliment_count = serializers.IntegerField(read_only=True, allow_null=True)
    trr_count = serializers.IntegerField(read_only=True, allow_null=True)
    major_award_count = serializers.IntegerField(read_only=True, allow_null=True)
    honorable_mention_percentile = serializers.FloatField(read_only=True, allow_null=True)
