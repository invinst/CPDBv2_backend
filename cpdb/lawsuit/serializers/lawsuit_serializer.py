import pytz

from rest_framework import serializers

from shared.serializer import NoNullSerializer, OfficerPercentileSerializer


class PaymentSerializer(NoNullSerializer):
    payee = serializers.CharField()
    settlement = serializers.DecimalField(max_digits=16, decimal_places=2, allow_null=True)
    legal_fees = serializers.DecimalField(max_digits=16, decimal_places=2, allow_null=True)


class TotalPaymentSerializer(NoNullSerializer):
    total = serializers.DecimalField(max_digits=16, decimal_places=2, allow_null=True)
    total_settlement = serializers.DecimalField(max_digits=16, decimal_places=2, allow_null=True)
    total_legal_fees = serializers.DecimalField(max_digits=16, decimal_places=2, allow_null=True)


class OfficerSerializer(OfficerPercentileSerializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    allegation_count = serializers.IntegerField()
    sustained_count = serializers.IntegerField()
    birth_year = serializers.IntegerField()
    race = serializers.CharField()
    gender = serializers.CharField()
    lawsuit_count = serializers.SerializerMethodField()
    lawsuit_payment = serializers.SerializerMethodField()

    def get_lawsuit_count(self, obj):
        return obj.lawsuit_set.count()

    def get_lawsuit_payment(self, obj):
        lawsuit_payment = 0
        for lawsuit in obj.lawsuit_set.all():
            for payment in lawsuit.payments.all():
                lawsuit_payment += payment.settlement or 0
                lawsuit_payment += payment.legal_fees or 0
        return str(lawsuit_payment)


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
    address = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)
    plaintiffs = PlaintiffSerializer(many=True)
    officers = serializers.SerializerMethodField()
    interactions = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    misconducts = serializers.SerializerMethodField()
    violences = serializers.SerializerMethodField()
    outcomes = serializers.SerializerMethodField()
    payments = PaymentSerializer(many=True)
    point = serializers.SerializerMethodField()
    total_payments = TotalPaymentSerializer()
    attachments = AttachmentFileSerializer(source='attachment_files', many=True)

    @staticmethod
    def _get_names(obj, attr):
        return [item.name for item in getattr(obj, attr).all()]

    def get_address(self, obj):
        add1 = obj.add1.strip()
        add2 = obj.add2.strip()
        city = obj.city.strip()
        return ', '.join(filter(None, [' '.join(filter(None, [add1, add2])), city]))

    def get_interactions(self, obj):
        return self._get_names(obj, 'interactions')

    def get_services(self, obj):
        return self._get_names(obj, 'services')

    def get_misconducts(self, obj):
        return self._get_names(obj, 'misconducts')

    def get_violences(self, obj):
        return self._get_names(obj, 'violences')

    def get_outcomes(self, obj):
        return self._get_names(obj, 'outcomes')

    def get_point(self, obj):
        if obj.point is not None:
            return {'lon': obj.point.x, 'lat': obj.point.y}
        else:
            return None

    def get_officers(self, obj):
        officers = obj.officers.prefetch_related('lawsuit_set', 'lawsuit_set__payments')
        return OfficerSerializer(officers, many=True).data
