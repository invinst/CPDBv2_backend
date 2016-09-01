from rest_framework import serializers

# from wagtail.api.v2 import serializers as wagtail_serializers

from landing_page.models import LandingPage
from faq.serializers import FAQSerializer
from story.serializers import StorySerializer


class LandingPageSerializer(serializers.ModelSerializer):
    reports = serializers.SerializerMethodField()
    faqs = serializers.SerializerMethodField()

    class Meta:
        model = LandingPage
        fields = ('id', 'reports', 'faqs')

    def get_reports(self, obj):
        return StorySerializer([obj.report1, obj.report2, obj.report3], many=True).data

    def get_faqs(self, obj):
        return FAQSerializer([obj.faq1, obj.faq2, obj.faq3], many=True).data
