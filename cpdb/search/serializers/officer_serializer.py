from rest_framework import serializers

from shared.serializer import NoNullSerializer


class OfficerSerializer(NoNullSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='full_name')
    race = serializers.CharField()
    gender = serializers.CharField(source='gender_display', read_only=True)
    allegation_count = serializers.IntegerField()
    sustained_count = serializers.IntegerField()
    birth_year = serializers.IntegerField()
    type = serializers.SerializerMethodField()
    rank = serializers.CharField()

    def get_type(self, obj):
        return 'OFFICER'
