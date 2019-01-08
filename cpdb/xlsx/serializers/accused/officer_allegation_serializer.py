from rest_framework.serializers import (
    Serializer, CharField, DateTimeField, BooleanField, IntegerField, DateField, NullBooleanField
)


class OfficerAllegationExcelSerializer(Serializer):
    # from allegation
    crid = CharField(source='allegation.crid')
    address = CharField(allow_blank=True, source='allegation.address')
    old_complaint_address = CharField(allow_null=True, source='allegation.old_complaint_address')
    incident_date = DateTimeField(format='%Y-%m-%d', allow_null=True, source='allegation.incident_date')
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
