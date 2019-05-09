from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from data.models import Allegation, Officer
from pinboard.models import Pinboard
from shared.serializer import NoNullSerializer
from trr.models import TRR


class PinboardSerializer(ModelSerializer, NoNullSerializer):
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
            'description',
        )


class OrderedPinboardSerializer(ModelSerializer, NoNullSerializer):
    id = serializers.CharField(min_length=8, max_length=8, read_only=True)
    officer_ids = serializers.ListField(child=serializers.IntegerField())
    crids = serializers.ListField(child=serializers.CharField())
    trr_ids = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Pinboard
        fields = (
            'id',
            'title',
            'officer_ids',
            'crids',
            'trr_ids',
            'description',
        )
