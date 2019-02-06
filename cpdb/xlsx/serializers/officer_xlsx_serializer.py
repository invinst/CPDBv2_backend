from rest_framework.serializers import Serializer, CharField, IntegerField, DateField, FloatField


class OfficerXlsxSerializer(Serializer):
    name = CharField(source='full_name')
    gender = CharField(source='gender_display', allow_blank=True)
    race = CharField()
    appointed_date = DateField(allow_null=True)
    resignation_date = DateField(allow_null=True)
    rank = CharField(allow_blank=True)
    birth_year = IntegerField(allow_null=True)
    active = CharField()

    complaint_percentile = FloatField(allow_null=True)
    civilian_allegation_percentile = FloatField(allow_null=True)
    internal_allegation_percentile = FloatField(allow_null=True)
    trr_percentile = FloatField(allow_null=True)
    honorable_mention_percentile = FloatField(allow_null=True)
    allegation_count = IntegerField(allow_null=True)
    sustained_count = IntegerField(allow_null=True)
    honorable_mention_count = IntegerField(allow_null=True)
    unsustained_count = IntegerField(allow_null=True)
    discipline_count = IntegerField(allow_null=True)
    civilian_compliment_count = IntegerField(allow_null=True)
    trr_count = IntegerField(allow_null=True)
    major_award_count = IntegerField(allow_null=True)
    current_badge = CharField(allow_null=True)
    last_unit = CharField(allow_null=True, source='last_unit.unit_name')
    current_salary = IntegerField(allow_null=True)


class CoaccusedOfficerXlsxSerializer(OfficerXlsxSerializer):
    coaccusal_count = IntegerField()
