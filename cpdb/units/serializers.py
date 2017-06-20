from rest_framework import serializers


class UnitSummarySerializer(serializers.Serializer):
    unit_name = serializers.CharField()
    member_records = serializers.SerializerMethodField()
    complaint_records = serializers.SerializerMethodField()

    def get_member_records(self, obj):
        return {
            'active_members': obj.active_member_count,
            'total': obj.member_count,
            'facets': [
                {'name': 'race', 'entries': obj.member_race_aggregation},
                {'name': 'age', 'entries': obj.member_age_aggregation},
                {'name': 'gender', 'entries': obj.member_gender_aggregation}
            ]
        }

    def get_complaint_records(self, obj):
        return {
            'count': obj.complaint_count,
            'sustained_count': obj.sustained_count,
            'facets': [
                {'name': 'category', 'entries': obj.complaint_category_aggregation},
                {'name': 'race', 'entries': obj.complainant_race_aggregation},
                {'name': 'age', 'entries': obj.complainant_age_aggregation},
                {'name': 'gender', 'entries': obj.complainant_gender_aggregation}
            ]
        }
