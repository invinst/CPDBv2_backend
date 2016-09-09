from rest_framework import serializers

from wagtail.api.v2 import serializers as wagtail_serializers

from faq.models import FAQ, FAQPage


class FAQSerializer(serializers.ModelSerializer):
    body = wagtail_serializers.StreamField()

    class Meta:
        model = FAQ
        fields = ('id', 'title', 'body')


class FAQPageSerializer(serializers.ModelSerializer):
    body = wagtail_serializers.StreamField()

    class Meta:
        model = FAQPage
        fields = ('id', 'title', 'body')
