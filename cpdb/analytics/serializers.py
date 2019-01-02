from rest_framework import serializers

from .models import Event, SearchTracking


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'name', 'data')


class SearchTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchTracking
        fields = ('id', 'query', 'usages', 'results', 'query_type', 'last_entered')
