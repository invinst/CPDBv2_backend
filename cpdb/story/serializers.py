from rest_framework import serializers

from wagtail.api.v2 import serializers as wagtail_serializers

from story.models import Story, Newspaper, StoryPage


class NewspaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newspaper


class StorySerializer(serializers.ModelSerializer):
    body = wagtail_serializers.StreamField()
    newspaper = NewspaperSerializer(required=False)
    image_url = serializers.SerializerMethodField()
    canonical_url = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = ('id', 'title', 'canonical_url', 'newspaper', 'post_date', 'image_url', 'body')

    def get_image_url(self, obj):
        if obj.image:
            return {
                '480_320': obj.image.get_rendition('min-480x320').url
            }

        return {}

    def get_canonical_url(self, obj):
        return obj.canonical_url


class StoryPageSerializer(serializers.ModelSerializer):
    body = wagtail_serializers.StreamField()
    image_url = serializers.SerializerMethodField()
    canonical_url = serializers.SerializerMethodField()

    class Meta:
        model = StoryPage
        fields = (
            'id', 'title', 'publication_name', 'publication_short_url', 'canonical_url',
            'post_date', 'image_url', 'body')

    def get_image_url(self, obj):
        if obj.image:
            return {
                '480_320': obj.image.get_rendition('min-480x320').url
            }

        return {}

    def get_canonical_url(self, obj):
        return obj.canonical_url
