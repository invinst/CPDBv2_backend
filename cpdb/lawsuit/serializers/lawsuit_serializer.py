import pytz

from django.db.models import Sum, Count

from rest_framework import serializers

from shared.serializer import NoNullSerializer, OfficerPercentileSerializer


class PaymentSerializer(NoNullSerializer):
    payee = serializers.CharField()
    settlement = serializers.DecimalField(max_digits=16, decimal_places=2, allow_null=True)
    legal_fees = serializers.DecimalField(max_digits=16, decimal_places=2, allow_null=True)


class OfficerSerializer(OfficerPercentileSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    allegation_count = serializers.IntegerField()
    sustained_count = serializers.IntegerField()
    birth_year = serializers.IntegerField()
    race = serializers.CharField()
    gender = serializers.CharField(source='gender_display')
    rank = serializers.CharField()
    lawsuit_count = serializers.SerializerMethodField()
    total_lawsuit_settlements = serializers.DecimalField(max_digits=16, decimal_places=2, allow_null=True)

    def get_lawsuit_count(self, obj):
        return obj.lawsuits.count()


class PlaintiffSerializer(NoNullSerializer):
    name = serializers.CharField()


class AttachmentFileSerializer(NoNullSerializer):
    id = serializers.CharField()
    title = serializers.CharField()
    file_type = serializers.CharField()
    url = serializers.CharField()
    preview_image_url = serializers.CharField()


class LawsuitSerializer(NoNullSerializer):
    case_no = serializers.CharField()
    summary = serializers.CharField()
    primary_cause = serializers.CharField()
    address = serializers.CharField()
    location = serializers.CharField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)
    plaintiffs = PlaintiffSerializer(many=True)
    officers = serializers.SerializerMethodField()
    interactions = serializers.ListField(child=serializers.CharField())
    services = serializers.ListField(child=serializers.CharField())
    misconducts = serializers.ListField(child=serializers.CharField())
    violences = serializers.ListField(child=serializers.CharField())
    outcomes = serializers.ListField(child=serializers.CharField())
    payments = PaymentSerializer(many=True)
    point = serializers.SerializerMethodField()
    attachment = serializers.SerializerMethodField()
    total_payments = serializers.DecimalField(max_digits=16, decimal_places=2, allow_null=True)
    total_settlement = serializers.DecimalField(max_digits=16, decimal_places=2, allow_null=True)
    total_legal_fees = serializers.DecimalField(max_digits=16, decimal_places=2, allow_null=True)

    def get_point(self, obj):
        if obj.point is not None:
            return {'lon': obj.point.x, 'lat': obj.point.y}
        else:
            return None

    def get_officers(self, obj):
        officers = obj.officers.annotate(
            total_lawsuit_settlements=Sum('lawsuits__total_payments'),
        ).prefetch_related('lawsuits')
        return OfficerSerializer(officers, many=True).data

    def get_attachment(self, obj):
        attachment = obj.attachment_files.first()
        return AttachmentFileSerializer(attachment).data if attachment else None
