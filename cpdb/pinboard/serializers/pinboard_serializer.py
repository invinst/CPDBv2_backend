from rest_framework import serializers

from data.models import Allegation, Officer
from pinboard.models import Pinboard
from pinboard.serializers.allegation_card_serializer import AllegationCardSerializer
from pinboard.serializers.document_card_serializer import DocumentCardSerializer
from pinboard.serializers.officer_card_serializer import OfficerCardSerializer
from shared.serializer import NoNullSerializer
from trr.models import TRR


class PinboardSerializer(NoNullSerializer):
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
    relevant_documents = DocumentCardSerializer(many=True)
    relevant_coaccusals = OfficerCardSerializer(many=True)
    relevant_complaints = AllegationCardSerializer(many=True)

    class Meta:
        model = Pinboard
        fields = (
            'id',
            'title',
            'officer_ids',
            'crids',
            'trr_ids',
            'description',
            'relevant_documents',
            'relevant_coaccusals',
            'relevant_complaints',
        )
