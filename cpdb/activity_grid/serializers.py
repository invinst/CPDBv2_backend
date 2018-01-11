from rest_framework import serializers


class OfficerCardSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    visual_token_background_color = serializers.CharField()
    full_name = serializers.CharField()
    complaint_count = serializers.IntegerField(source='allegation_count')
    sustained_count = serializers.IntegerField()
    birth_year = serializers.IntegerField()
    race = serializers.CharField()
    gender = serializers.CharField(source='gender_display')


class ActivityCardSerializer(serializers.Serializer):
    def to_representation(self, obj):
        if obj.officer:
            result = OfficerCardSerializer(obj.officer).data
            return result
