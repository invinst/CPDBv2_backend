from rest_framework import serializers

from data.models import Officer, Allegation
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

    class Meta:
        model = Pinboard
        fields = (
            'id',
            'title',
            'officer_ids',
            'crids',
            'description'
        )
