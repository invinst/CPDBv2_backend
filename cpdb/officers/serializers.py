from rest_framework import serializers


class OfficerSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    unit = serializers.CharField(source='last_unit')
    date_of_appt = serializers.DateField(source='appointed_date', format='%Y-%m-%d')
    date_of_resignation = serializers.DateField(source='resignation_date', format='%Y-%m-%d')
    active = serializers.SerializerMethodField()
    rank = serializers.CharField()
    full_name = serializers.CharField()
    race = serializers.CharField()
    badge = serializers.CharField(source='current_badge')
    gender = serializers.CharField(source='gender_display')
    complaint_records = serializers.SerializerMethodField()
    birth_year = serializers.IntegerField()

    def get_complaint_records(self, obj):
        return {
            'count': obj.allegation_count,
            'sustained_count': obj.sustained_count,
            'facets': [
                {'name': 'category', 'entries': obj.complaint_category_aggregation},
                {'name': 'complainant race', 'entries': obj.complainant_race_aggregation},
                {'name': 'complainant age', 'entries': obj.complainant_age_aggregation},
                {'name': 'complainant gender', 'entries': obj.complainant_gender_aggregation},
            ],
            'items': obj.total_complaints_aggregation
        }

    def get_active(self, obj):
        return obj.get_active_display()


class OfficerMetricsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    allegation_count = serializers.IntegerField()
    complaint_percentile = serializers.FloatField()
    honorable_mention_count = serializers.IntegerField()
    sustained_count = serializers.IntegerField()
    discipline_count = serializers.IntegerField()
    civilian_compliment_count = serializers.IntegerField()


class CRTimelineSerializer(serializers.Serializer):
    officer_id = serializers.IntegerField()
    date_sort = serializers.DateField(source='start_date', format=None)
    date = serializers.DateField(source='start_date', format='%Y-%m-%d')
    year_sort = serializers.IntegerField(source='start_date.year')
    priority_sort = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()
    crid = serializers.CharField()
    category = serializers.SerializerMethodField()
    subcategory = serializers.CharField()
    finding = serializers.CharField(source='final_finding_display')
    coaccused = serializers.IntegerField(source='coaccused_count')
    race = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()

    def get_category(self, obj):
        return obj.category if obj.category else 'Unknown'

    def get_kind(self, obj):
        return 'CR'

    def get_priority_sort(self, obj):
        return 40

    def get_race(self, obj):
        return obj.allegation.complainant_races

    def get_age(self, obj):
        return obj.allegation.complainant_age_groups

    def get_gender(self, obj):
        return obj.allegation.complainant_genders


class UnitChangeTimelineSerializer(serializers.Serializer):
    officer_id = serializers.IntegerField()
    date_sort = serializers.DateField(source='effective_date', format=None)
    priority_sort = serializers.SerializerMethodField()
    date = serializers.DateField(source='effective_date', format='%Y-%m-%d')
    year_sort = serializers.IntegerField(source='effective_date.year')
    kind = serializers.SerializerMethodField()
    unit_name = serializers.CharField()

    def get_kind(self, obj):
        return 'UNIT_CHANGE'

    def get_priority_sort(self, obj):
        return 30


class JoinedTimelineSerializer(serializers.Serializer):
    officer_id = serializers.IntegerField(source='id')
    date_sort = serializers.DateField(source='appointed_date', format=None)
    priority_sort = serializers.SerializerMethodField()
    date = serializers.DateField(source='appointed_date', format='%Y-%m-%d')
    year_sort = serializers.IntegerField(source='appointed_date.year')
    kind = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return 'JOINED'

    def get_priority_sort(self, obj):
        return 10


class TimelineSerializer(serializers.Serializer):
    def to_representation(self, obj):
        result = obj.to_dict()
        result.pop('officer_id')
        result.pop('date_sort')
        result.pop('year_sort')
        result.pop('priority_sort')
        return result


class TimelineMinimapSerializer(serializers.Serializer):
    _KIND_MAPPINGS = {
        'UNIT_CHANGE': 'Unit',
        'JOINED': 'Joined',
    }

    year = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()

    def get_year(self, obj):
        return int(obj.date[:4])  # date is in ISO format: YYYY-MM-DD

    def get_kind(self, obj):
        return self._KIND_MAPPINGS.get(obj.kind, obj.kind)
