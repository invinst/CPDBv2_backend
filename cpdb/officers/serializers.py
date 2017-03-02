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
                {'name': 'categories', 'entries': obj.complaint_category_aggregation},
                {'name': 'races', 'entries': obj.complainant_race_aggregation},
                {'name': 'ages', 'entries': obj.complainant_age_aggregation},
                {'name': 'genders', 'entries': obj.complainant_gender_aggregation},
            ]
        }
