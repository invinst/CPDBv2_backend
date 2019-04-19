from rest_framework import serializers

from shared.serializer import NoNullSerializer
from data.models import Officer, Allegation
from trr.models import TRR
from .models import Pinboard


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

    class Meta:
        model = Pinboard
        fields = (
            'id',
            'title',
            'officer_ids',
            'crids',
            'trr_ids',
            'description'
        )


class VictimSerializer(NoNullSerializer):
    gender = serializers.CharField(source='gender_display')
    race = serializers.CharField()
    age = serializers.IntegerField()


class CRPinboardSerializer(NoNullSerializer):
    date = serializers.SerializerMethodField()
    crid = serializers.CharField()
    category = serializers.SerializerMethodField()
    coaccused_count = serializers.IntegerField()
    kind = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()
    victims = VictimSerializer(many=True)

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
    taser = serializers.NullBooleanField()
    firearm_used = serializers.NullBooleanField()
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


class PinboardComplaintSerializer(serializers.ModelSerializer):
    most_common_category = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')

    def get_point(self, obj):
        return {'lon': obj.point.x, 'lat': obj.point.y} if obj.point is not None else None

    def get_most_common_category(self, obj):
        return obj.most_common_category.category if obj.most_common_category is not None else ''

    class Meta:
        model = Allegation
        fields = (
            'crid',
            'incident_date',
            'point',
            'most_common_category'
        )


class PinboardTRRSerializer(serializers.ModelSerializer):
    trr_datetime = serializers.DateTimeField(format='%Y-%m-%d')
    point = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    def get_point(self, obj):
        return {'lon': obj.point.x, 'lat': obj.point.y} if obj.point is not None else None

    def get_category(self, obj):
        return obj.force_types[0] if len(obj.force_types) > 0 else 'Unknown'

    class Meta:
        model = TRR
        fields = (
            'id',
            'trr_datetime',
            'category',
            'point',
        )
