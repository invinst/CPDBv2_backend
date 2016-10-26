from django.core.management.base import BaseCommand

from cms.serializers import LandingPageSerializer, ReportPageSerializer


class Command(BaseCommand):
    def handle(self, *args, **options):
        landing_page_serializer = LandingPageSerializer(data=LandingPageSerializer().fake_data())
        landing_page_serializer.is_valid()
        landing_page_serializer.save()
        for _ in range(16):
            report_page_serializer = ReportPageSerializer(data=ReportPageSerializer().fake_data())
            report_page_serializer.is_valid()
            report_page_serializer.save()
