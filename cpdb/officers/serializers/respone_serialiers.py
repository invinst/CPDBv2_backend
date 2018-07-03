from rest_framework import serializers


class TimelineSerializer(serializers.Serializer):
    def to_representation(self, obj):
        remove_keys = ['officer_id', 'date_sort', 'year_sort', 'priority_sort']
        return {key: value for key, value in obj.to_dict().iteritems() if key not in remove_keys}


class NewTimelineSerializer(serializers.Serializer):
    def to_representation(self, obj):
        remove_keys = ['officer_id', 'date_sort', 'priority_sort']
        return {key: value for key, value in obj.to_dict().iteritems() if key not in remove_keys}


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
