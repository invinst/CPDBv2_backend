from rest_framework import serializers

from data.models import Officer, Allegation
from .models import Pinboard


class PinboardSerializer(serializers.ModelSerializer):
    id = serializers.CharField(
        min_length=8,
        max_length=8,
        read_only=True
    )
    crids = serializers.SlugRelatedField(
        source='allegations',
        many=True,
        queryset=Allegation.objects.all(),
        slug_field='crid'
    )
    officer_ids = serializers.SlugRelatedField(
        source='officers',
        many=True,
        queryset=Officer.objects.all(),
        slug_field='id'
    )

    class Meta:
        model = Pinboard
        fields = (
            'id',
            'title',
            'officer_ids',
            'crids',
            'description'
        )
