from rest_framework import serializers


class OfficerSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    unit = serializers.CharField(source='last_unit')
    date_of_appt = serializers.DateField(source='appointed_date', format='%Y-%m-%d')
    rank = serializers.CharField()
    full_name = serializers.CharField()
    race = serializers.CharField()
    badge = serializers.CharField(source='current_badge')
    gender = serializers.CharField(source='gender_display')
    complaint_records = serializers.SerializerMethodField()

    def get_complaint_records(self, obj):
        return {
            'count': obj.allegation_count,
            'facets': [
                {'name': 'category', 'entries': obj.complaint_category_aggregation},
                {'name': 'race', 'entries': obj.complainant_race_aggregation},
                {'name': 'age', 'entries': obj.complainant_age_aggregation},
                {'name': 'gender', 'entries': obj.complainant_gender_aggregation},
            ]
        }


class CRTimelineSerializer(serializers.Serializer):
    officer_id = serializers.IntegerField()
    date_sort = serializers.DateField(source='start_date', format=None)
    date = serializers.DateField(source='start_date', format='%Y-%m-%d')
    kind = serializers.SerializerMethodField()
    crid = serializers.CharField()
    category = serializers.CharField()
    subcategory = serializers.CharField()
    finding = serializers.CharField(source='final_finding_display')
    coaccused = serializers.IntegerField(source='coaccused_count')

    def get_kind(self, obj):
        return 'CR'


class UnitChangeTimelineSerializer(serializers.Serializer):
    officer_id = serializers.IntegerField()
    date_sort = serializers.DateField(source='effective_date', format=None)
    date = serializers.DateField(source='effective_date', format='%Y-%m-%d')
    kind = serializers.SerializerMethodField()
    unit_name = serializers.CharField()

    def get_kind(self, obj):
        return 'UNIT_CHANGE'


class TimelineSerializer(serializers.Serializer):
    def to_representation(self, obj):
        result = obj.to_dict()
        result.pop('officer_id')
        result.pop('date_sort')
        return result
