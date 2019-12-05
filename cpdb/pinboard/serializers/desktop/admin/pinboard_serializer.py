import pytz
from rest_framework import serializers

from pinboard.serializers.desktop.admin.allegation_serializer import AllegationSerializer
from pinboard.serializers.desktop.admin.officer_serializer import OfficerSerializer
from pinboard.serializers.desktop.admin.trr_serializer import TRRSerializer
from shared.serializer import NoNullSerializer


class PinboardSerializer(NoNullSerializer):
    id = serializers.CharField(min_length=8, max_length=8, read_only=True)
    title = serializers.CharField()
    description = serializers.CharField()
    created_at = serializers.DateTimeField(default_timezone=pytz.utc)
    officers_count = serializers.SerializerMethodField()
    allegations_count = serializers.SerializerMethodField()
    trrs_count = serializers.SerializerMethodField()
    officers = serializers.SerializerMethodField()
    allegations = serializers.SerializerMethodField()
    trrs = serializers.SerializerMethodField()
    child_pinboard_count = serializers.IntegerField()

    def get_officers_count(self, obj):
        return obj.officers.count()

    def get_allegations_count(self, obj):
        return obj.allegations.count()

    def get_trrs_count(self, obj):
        return obj.trrs.count()

    def get_officers(self, obj):
        return OfficerSerializer(reversed(obj.officers.all()), many=True).data

    def get_allegations(self, obj):
        return AllegationSerializer(reversed(obj.allegations.all()), many=True).data

    def get_trrs(self, obj):
        return TRRSerializer(reversed(obj.trrs.all()), many=True).data
