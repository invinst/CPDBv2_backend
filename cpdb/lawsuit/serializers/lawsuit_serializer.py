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


class PlaintiffSerializer(NoNullSerializer):
    name = serializers.CharField()


class LawsuitSerializer(NoNullSerializer):
    case_no = serializers.CharField()
    summary = serializers.CharField()
    address = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)
    plaintiffs = PlaintiffSerializer(many=True)
    officers = OfficerSerializer(many=True)
    interactions = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    misconducts = serializers.SerializerMethodField()
    violences = serializers.SerializerMethodField()
    outcomes = serializers.SerializerMethodField()
    payments = PaymentSerializer(many=True)
    total_payments = TotalPaymentSerializer()

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
