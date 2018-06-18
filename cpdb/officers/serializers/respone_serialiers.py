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


class OfficerMobileSerializer(serializers.Serializer):
    officer_id = serializers.IntegerField(source='id')
    full_name = serializers.CharField(max_length=255)
    percentiles = OfficerYearlyPercentileSerializer(many=True, allow_null=True)
