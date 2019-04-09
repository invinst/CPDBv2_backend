from rest_framework import serializers

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


class PinboardComplaintSerializer(serializers.ModelSerializer):
    most_common_category = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')

    def get_point(self, obj):
        if obj.point is not None:
            return {'lon': obj.point.x, 'lat': obj.point.y}
        return None

    def get_most_common_category(self, obj):
        if obj.most_common_category is not None:
            return obj.most_common_category.category
        return ''

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
    category = serializers.SerializerMethodField()

    def get_category(self, obj):
        return obj.force_types[0] if len(obj.force_types) > 0 else 'Unknown'

    class Meta:
        model = TRR
        fields = (
            'id',
            'trr_datetime',
            'category',
        )
