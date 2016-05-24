from rest_framework import serializers

from wagtail.api.v2 import serializers as wagtail_serializers

from story.models import StoryPage, Newspaper


class NewspaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newspaper


class StorySerializer(serializers.ModelSerializer):
    body = wagtail_serializers.StreamField()
    newspaper = NewspaperSerializer()

    class Meta:
        model = StoryPage
        fields = ('id', 'title', 'newspaper', 'post_date', 'body')
