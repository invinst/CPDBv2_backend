from rest_framework import serializers

from .base import CherryPickSerializer
from data.constants import MEDIA_TYPE_VIDEO, MEDIA_TYPE_AUDIO, MEDIA_TYPE_DOCUMENT


class CoaccusedDesktopSerializer(CherryPickSerializer):
    class Meta(object):
        fields = (
            'id',
            'full_name',
            'gender',
            'race',
            'rank',
            'age',
            'allegation_count',
            'sustained_count',
            'final_outcome',
            'category',
            'percentile_allegation',
            'percentile_allegation_civilian',
            'percentile_allegation_internal',
            'percentile_trr'
        )


class InvestigatorDesktopSerializer(CherryPickSerializer):
    class Meta(object):
        fields = (
            'involved_type',
            'officer_id',
            'full_name',
            'current_rank',
            'percentile_allegation_civilian',
            'percentile_allegation_internal',
            'percentile_trr'
        )


class PoliceWitnessDesktopSerializer(CherryPickSerializer):
    class Meta(object):
        fields = (
            'involved_type',
            'officer_id',
            'full_name',
            'allegation_count',
            'sustained_count',
            'percentile_allegation_civilian',
            'percentile_allegation_internal',
            'percentile_trr'
        )


class CRDesktopSerializer(serializers.Serializer):
    crid = serializers.CharField()
    coaccused = CoaccusedDesktopSerializer(many=True, default=[])
    complainants = serializers.JSONField(default=[])
    victims = serializers.JSONField(default=[])
    summary = serializers.CharField(required=False)
    point = serializers.JSONField(required=False)
    incident_date = serializers.CharField(required=False)
    start_date = serializers.CharField(required=False)
    end_date = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    location = serializers.CharField(required=False)
    beat = serializers.CharField(required=False)
    involvements = serializers.SerializerMethodField()
    attachments = serializers.JSONField(default=[])

    def get_involvements(self, obj):
        serializer_map = {
            'investigator': InvestigatorDesktopSerializer,
            'police_witness': PoliceWitnessDesktopSerializer
        }
        return [
            serializer_map[involvement['involved_type']](involvement).data
            for involvement in obj.get('involvements', [])
        ]


class CoaccusedMobileSerializer(CherryPickSerializer):
    class Meta(object):
        fields = (
            'id',
            'full_name',
            'gender',
            'race',
            'final_finding',
            'recc_outcome',
            'final_outcome',
            'category',
            'subcategory',
            'start_date',
            'end_date'
        )


class AttachmentField(serializers.Field):
    def __init__(self, type, *args, **kwargs):
        super(AttachmentField, self).__init__(*args, **kwargs)
        self.type = type

    def to_representation(self, obj):
        return [
            {
                'title': attachment['title'],
                'url': attachment['url']
            } for attachment in obj if attachment['file_type'] == self.type
        ]


class InvestigatorMobileSerializer(serializers.Serializer):
    involved_type = serializers.SerializerMethodField()
    officers = serializers.SerializerMethodField()

    def get_involved_type(self, obj):
        return 'investigator'

    def get_officers(self, obj):
        return [
            {
                'id': involvement['officer_id'],
                'abbr_name': involvement['abbr_name'],
                'extra_info': '%d case(s)' % involvement['num_cases']
            }
            for involvement in obj.get('involvements', [])
            if involvement['involved_type'] == 'investigator'
        ]


class PoliceWitnessMobileSerializer(serializers.Serializer):
    involved_type = serializers.SerializerMethodField()
    officers = serializers.SerializerMethodField()

    def get_involved_type(self, obj):
        return 'police witnesses'

    def get_officers(self, obj):
        return [
            {
                'id': involvement['officer_id'],
                'abbr_name': involvement['abbr_name'],
                'extra_info': ', '.join([involvement['gender'], involvement['race']])
            }
            for involvement in obj.get('involvements', [])
            if involvement['involved_type'] == 'police_witness'
        ]


class CRMobileSerializer(serializers.Serializer):
    crid = serializers.CharField()
    coaccused = CoaccusedMobileSerializer(many=True)
    complainants = serializers.JSONField(default=[])
    point = serializers.SerializerMethodField(required=False)
    incident_date = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    location = serializers.CharField(required=False)
    beat = serializers.SerializerMethodField()
    involvements = serializers.SerializerMethodField()
    audios = AttachmentField(source='attachments', type=MEDIA_TYPE_AUDIO, default=[])
    videos = AttachmentField(source='attachments', type=MEDIA_TYPE_VIDEO, default=[])
    documents = AttachmentField(source='attachments', type=MEDIA_TYPE_DOCUMENT, default=[])

    def get_point(self, obj):
        point = obj.get('point', {
            'lon': None,
            'lat': None
        })
        return {
            'long': point['lon'],
            'lat': point['lat']
        }

    def get_beat(self, obj):
        return {
            'name': obj.get('beat', '')
        }

    def get_involvements(self, obj):
        return [
            InvestigatorMobileSerializer(obj).data,
            PoliceWitnessMobileSerializer(obj).data
        ]
