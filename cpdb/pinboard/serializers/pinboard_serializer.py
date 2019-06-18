from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from data.models import Allegation, Officer
from pinboard.models import Pinboard, ExamplePinboard
from pinboard.serializers.example_pinboard import ExamplePinboardSerializer
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
    example_pinboards = SerializerMethodField()

    def get_example_pinboards(self, obj):
        if obj.is_empty:
            return ExamplePinboardSerializer(ExamplePinboard.random(2), many=True).data
        else:
            return None

    class Meta:
        model = Pinboard
        fields = (
            'id',
            'title',
            'officer_ids',
            'crids',
            'trr_ids',
            'description',
            'example_pinboards',
        )


class OrderedPinboardSerializer(ModelSerializer, NoNullSerializer):
    id = serializers.CharField(min_length=8, max_length=8, read_only=True)
    officer_ids = serializers.ListField(child=serializers.IntegerField())
    crids = serializers.ListField(child=serializers.CharField())
    trr_ids = serializers.ListField(child=serializers.IntegerField())
    example_pinboards = SerializerMethodField()

    def get_example_pinboards(self, obj):
        if obj.is_empty:
            return ExamplePinboardSerializer(ExamplePinboard.random(2), many=True).data
        else:
            return None

    class Meta:
        model = Pinboard
        fields = (
            'id',
            'title',
            'officer_ids',
            'crids',
            'trr_ids',
            'description',
            'example_pinboards',
        )
