from rest_framework import serializers

from .models import SearchTracking


class SearchTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchTracking
        fields = '__all__'
