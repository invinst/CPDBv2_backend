from django.core.management.base import BaseCommand

from cms.serializers import LandingPageSerializer


class Command(BaseCommand):
    def handle(self, *args, **options):
        landing_page_serializer = LandingPageSerializer(data=LandingPageSerializer().fake_data())
        landing_page_serializer.is_valid()
        landing_page_serializer.save()
