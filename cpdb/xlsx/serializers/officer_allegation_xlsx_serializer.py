from rest_framework.serializers import (
    Serializer, CharField, DateTimeField, BooleanField, IntegerField, DateField, NullBooleanField, FloatField
)

import pytz


class OfficerAllegationXlsxSerializer(Serializer):
    # from allegation
    crid = CharField(source='allegation.crid')
    officer_name = CharField(allow_blank=True, source='officer.full_name')
    address = CharField(allow_blank=True, source='allegation.address')
    old_complaint_address = CharField(allow_null=True, source='allegation.old_complaint_address')
    incident_date = DateTimeField(
        format='%Y-%m-%d', allow_null=True, source='allegation.incident_date', default_timezone=pytz.utc
    )
    is_officer_complaint = BooleanField(source='allegation.is_officer_complaint')
    beat = CharField(source='allegation.beat.name', allow_null=True)
    coaccused_count = IntegerField(allow_null=True, source='allegation.coaccused_count')

    category = CharField(allow_null=True)
    subcategory = CharField(allow_null=True)
    start_date = DateField(allow_null=True)
    end_date = DateField(allow_null=True)
    recc_finding = CharField(allow_blank=True, source='recc_finding_display')
    recc_outcome = CharField(allow_blank=True)
    final_finding = CharField(allow_blank=True, source='final_finding_display')
    final_outcome = CharField(allow_blank=True)
    disciplined = NullBooleanField()


class OfficerFromAllegationOfficerXlsxSerializer(Serializer):
    crid = CharField(source='allegation.crid')
    name = CharField(source='officer.full_name')
    gender = CharField(source='officer.gender_display', allow_blank=True)
    race = CharField(source='officer.race')
    appointed_date = DateField(allow_null=True, source='officer.appointed_date')
    resignation_date = DateField(allow_null=True, source='officer.resignation_date')
    rank = CharField(allow_blank=True, source='officer.rank')
    birth_year = IntegerField(allow_null=True, source='officer.birth_year')
    active = CharField(source='officer.active')

    complaint_percentile = FloatField(allow_null=True, source='officer.complaint_percentile')
    civilian_allegation_percentile = FloatField(allow_null=True, source='officer.civilian_allegation_percentile')
    internal_allegation_percentile = FloatField(allow_null=True, source='officer.internal_allegation_percentile')
    trr_percentile = FloatField(allow_null=True, source='officer.trr_percentile')
    honorable_mention_percentile = FloatField(allow_null=True, source='officer.honorable_mention_percentile')
    allegation_count = IntegerField(allow_null=True, source='officer.allegation_count')
    sustained_count = IntegerField(allow_null=True, source='officer.sustained_count')
    honorable_mention_count = IntegerField(allow_null=True, source='officer.honorable_mention_count')
    unsustained_count = IntegerField(allow_null=True, source='officer.unsustained_count')
    discipline_count = IntegerField(allow_null=True, source='officer.discipline_count')
    civilian_compliment_count = IntegerField(allow_null=True, source='officer.civilian_compliment_count')
    trr_count = IntegerField(allow_null=True, source='officer.trr_count')
    major_award_count = IntegerField(allow_null=True, source='officer.major_award_count')
    current_badge = CharField(allow_null=True, source='officer.current_badge')
    last_unit = CharField(allow_null=True, source='officer.last_unit.unit_name')
    current_salary = IntegerField(allow_null=True, source='officer.current_salary')
