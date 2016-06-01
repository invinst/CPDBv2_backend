from rest_framework import serializers

from wagtail.api.v2 import serializers as wagtail_serializers

from story.models import StoryPage


class FAQSerializer(serializers.ModelSerializer):
    body = wagtail_serializers.StreamField()

    class Meta:
        model = StoryPage
        fields = ('id', 'title', 'body')
