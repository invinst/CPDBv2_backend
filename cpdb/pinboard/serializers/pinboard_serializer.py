from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

import pytz

from data.models import Allegation, Officer
from pinboard.models import Pinboard
from pinboard.serializers.example_pinboard import ExamplePinboardSerializer
from shared.serializer import NoNullSerializer
from trr.models import TRR


class PinboardSerializer(NoNullSerializer):
    id = serializers.CharField(min_length=8, max_length=8, read_only=True)
    title = serializers.CharField()
    created_at = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)


class ListPinboardDetailSerializer(PinboardSerializer):
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


class PinboardDetailSerializer(ModelSerializer, NoNullSerializer):
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
    example_pinboards = ExamplePinboardSerializer(many=True, read_only=True)

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

    def __init__(self, instance=None, data=None, *args, **kwargs):
        if data is None:
            self.not_found_officer_ids = None
            self.not_found_crids = None
            self.not_found_trr_ids = None
            super(PinboardDetailSerializer, self).__init__(instance=instance, *args, **kwargs)
        else:
            officer_ids = [int(officer_id) for officer_id in data.get('officer_ids', [])]
            crids = data.get('crids', [])
            trr_ids = [int(trr_id) for trr_id in data.get('trr_ids', [])]

            found_officer_ids = Officer.objects.filter(id__in=officer_ids).values_list('id', flat=True)
            found_crids = Allegation.objects.filter(crid__in=crids).values_list('crid', flat=True)
            found_trr_ids = TRR.objects.filter(id__in=trr_ids).values_list('id', flat=True)

            self.not_found_officer_ids = [i for i in officer_ids if i not in found_officer_ids]
            self.not_found_crids = [i for i in crids if i not in found_crids]
            self.not_found_trr_ids = [i for i in trr_ids if i not in found_trr_ids]

            new_data = data.copy()
            new_data['officer_ids'] = [i for i in officer_ids if i in found_officer_ids]
            new_data['crids'] = [i for i in crids if i in found_crids]
            new_data['trr_ids'] = [i for i in trr_ids if i in found_trr_ids]
            super(PinboardDetailSerializer, self).__init__(instance=instance, data=new_data, *args, **kwargs)

    @property
    def data(self):
        _data = super(PinboardDetailSerializer, self).data
        if self.not_found_officer_ids or self.not_found_crids or self.not_found_trr_ids:
            _data['not_found_items'] = {
                'officer_ids': self.not_found_officer_ids,
                'crids': self.not_found_crids,
                'trr_ids': self.not_found_trr_ids,
            }
        return _data


class OrderedPinboardSerializer(ModelSerializer, NoNullSerializer):
    id = serializers.CharField(min_length=8, max_length=8, read_only=True)
    officer_ids = serializers.ListField(child=serializers.IntegerField())
    crids = serializers.ListField(child=serializers.CharField())
    trr_ids = serializers.ListField(child=serializers.IntegerField())
    example_pinboards = ExamplePinboardSerializer(many=True, read_only=True)

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
