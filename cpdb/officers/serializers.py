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
