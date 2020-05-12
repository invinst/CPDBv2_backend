from rest_framework import serializers

from app_config.models import VisualTokenColor


class VisualTokenColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisualTokenColor
        fields = ('color', 'text_color', 'lower_range', 'upper_range')
