from django.core.management.base import BaseCommand

from cms.serializers import ReportPageSerializer, FAQPageSerializer, get_slug_page_serializer
from cms.models import ReportPage, FAQPage, SlugPage


class Command(BaseCommand):
    def handle(self, *args, **options):
        for slug_page in SlugPage.objects.all():
            serializer_class = get_slug_page_serializer(slug_page)
            serializer = serializer_class(slug_page, data=serializer_class(slug_page).data)
            serializer.is_valid()
            serializer.save()

        for report in ReportPage.objects.all():
            serializer = ReportPageSerializer(report, data=ReportPageSerializer(report).data)
            serializer.is_valid()
            serializer.save()

        for faq in FAQPage.objects.all():
            serializer = FAQPageSerializer(faq, data=FAQPageSerializer(faq).data)
            serializer.is_valid()
            serializer.save()
