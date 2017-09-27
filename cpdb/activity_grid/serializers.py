from rest_framework import serializers


class OfficerCardSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    visual_token_background_color = serializers.CharField()
    full_name = serializers.CharField()


class ActivityCardSerializer(serializers.Serializer):
    def to_representation(self, obj):
        if obj.officer:
            result = OfficerCardSerializer(obj.officer).data
            return result
