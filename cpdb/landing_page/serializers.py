from rest_framework import serializers

# from wagtail.api.v2 import serializers as wagtail_serializers

from landing_page.models import LandingPage
from faq.serializers import FAQPageSerializer
from story.serializers import StoryPageSerializer


class LandingPageSerializer(serializers.ModelSerializer):
    reports = serializers.SerializerMethodField()
    faqs = serializers.SerializerMethodField()

    class Meta:
        model = LandingPage
        fields = (
            'id', 'reports', 'faqs', 'vftg_header', 'vftg_date', 'vftg_content', 'vftg_link',
            'hero_complaints_text', 'hero_use_of_force_text', 'page_title', 'description')

    def get_reports(self, obj):
        return StoryPageSerializer(obj.randomized_coverages(), many=True).data

    def get_faqs(self, obj):
        return FAQPageSerializer(obj.randomized_faqs(), many=True).data
