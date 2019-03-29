from rest_framework import serializers

from shared.serializer import NoNullSerializer, OfficerPercentileSerializer
from data.models import Officer, Allegation
from trr.models import TRR
from .models import Pinboard


class OfficerCardSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    coaccusal_count = serializers.IntegerField()
    percentile = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return ' '.join([obj.first_name, obj.last_name])

    def get_percentile(self, obj):
        return OfficerPercentileSerializer(obj).data

    class Meta:
        model = Officer
        fields = (
            'id',
            'rank',
            'full_name',
            'coaccusal_count',
            'percentile',
        )


class PinboardSerializer(serializers.ModelSerializer):
    id = serializers.CharField(
        min_length=8,
        max_length=8,
        read_only=True
    )
    crids = serializers.PrimaryKeyRelatedField(
        source='allegations',
        many=True,
        queryset=Allegation.objects.all()
    )
    officer_ids = serializers.PrimaryKeyRelatedField(
        source='officers',
        many=True,
        queryset=Officer.objects.all()
    )
    trr_ids = serializers.PrimaryKeyRelatedField(
        source='trrs',
        many=True,
        queryset=TRR.objects.all()
    )
    relevant_coaccusals = serializers.SerializerMethodField()

    def get_relevant_coaccusals(self, obj):
        return OfficerCardSerializer(obj.relevant_coaccusals, many=True).data

    class Meta:
        model = Pinboard
        fields = (
            'id',
            'title',
            'officer_ids',
            'crids',
            'trr_ids',
            'description',
            'relevant_coaccusals',
        )


class CRPinboardSerializer(NoNullSerializer):
    date = serializers.SerializerMethodField()
    crid = serializers.CharField()
    category = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return 'CR'

    def get_category(self, obj):
        return obj.most_common_category.category if obj.most_common_category else 'Unknown'

    def get_date(self, obj):
        return obj.incident_date.date().strftime(format='%Y-%m-%d')

    def get_point(self, obj):
        try:
            return {
                'lon': obj.point.x,
                'lat': obj.point.y
            }
        except AttributeError:
            return None


class TRRPinboardSerializer(NoNullSerializer):
    trr_id = serializers.IntegerField(source='id')
    date = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return 'FORCE'

    def get_date(self, obj):
        return obj.trr_datetime.date().strftime(format='%Y-%m-%d')

    def get_point(self, obj):
        try:
            return {
                'lon': obj.point.x,
                'lat': obj.point.y
            }
        except AttributeError:
            return None
