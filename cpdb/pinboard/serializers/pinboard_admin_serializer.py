import pytz
from rest_framework import serializers

from shared.serializer import NoNullSerializer, OfficerPercentileSerializer


class OfficerSerializer(OfficerPercentileSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='full_name')
    count = serializers.IntegerField(source='allegation_count')


class AllegationSerializer(NoNullSerializer):
    crid = serializers.CharField()
    category = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)

    def get_category(self, obj):
        try:
            return obj.most_common_category.category
        except AttributeError:
            return 'Unknown'


class TRRSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    trr_datetime = serializers.DateTimeField(format='%Y-%m-%d', default_timezone=pytz.utc)
    category = serializers.SerializerMethodField()

    def get_category(self, obj):
        force_types = [res.force_type for res in obj.actionresponse_set.all()]
        return force_types[0] if len(force_types) > 0 else 'Unknown'


class PinboardItemSerializer(NoNullSerializer):
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
