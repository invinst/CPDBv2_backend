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
            'sustained_count': obj.sustained_count,
            'facets': [
                {'name': 'category', 'entries': obj.complaint_category_aggregation},
                {'name': 'complainant race', 'entries': obj.complainant_race_aggregation},
                {'name': 'complainant age', 'entries': obj.complainant_age_aggregation},
                {'name': 'complainant gender', 'entries': obj.complainant_gender_aggregation},
            ]
        }


class CRTimelineSerializer(serializers.Serializer):
    officer_id = serializers.IntegerField()
    date_sort = serializers.DateField(source='start_date', format=None)
    date = serializers.DateField(source='start_date', format='%Y-%m-%d')
    year_sort = serializers.IntegerField(source='start_date.year')
    kind = serializers.SerializerMethodField()
    crid = serializers.CharField()
    category = serializers.CharField()
    subcategory = serializers.CharField()
    finding = serializers.CharField()
    coaccused = serializers.IntegerField(source='coaccused_count')

    def get_kind(self, obj):
        return 'CR'


class UnitChangeTimelineSerializer(serializers.Serializer):
    officer_id = serializers.IntegerField()
    date_sort = serializers.DateField(source='effective_date', format=None)
    date = serializers.DateField(source='effective_date', format='%Y-%m-%d')
    year_sort = serializers.IntegerField(source='effective_date.year')
    kind = serializers.SerializerMethodField()
    unit_name = serializers.CharField()

    def get_kind(self, obj):
        return 'UNIT_CHANGE'


class JoinedTimelineSerializer(serializers.Serializer):
    officer_id = serializers.IntegerField(source='id')
    date_sort = serializers.DateField(source='appointed_date', format=None)
    date = serializers.DateField(source='appointed_date', format='%Y-%m-%d')
    year_sort = serializers.IntegerField(source='appointed_date.year')
    kind = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return 'JOINED'


class TimelineSerializer(serializers.Serializer):
    def to_representation(self, obj):
        result = obj.to_dict()
        result.pop('officer_id')
        result.pop('date_sort')
        result.pop('year_sort')
        return result
