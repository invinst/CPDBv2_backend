from django.core.management.base import BaseCommand

from cms.serializers import (
    LandingPageSerializer,
    OfficerPageSerializer,
    CRPageSerializer,
    TRRPageSerializer,
    get_slug_page_serializer
)
from cms.models import SlugPage


CSM_SERIALIZERS = [LandingPageSerializer, OfficerPageSerializer, CRPageSerializer, TRRPageSerializer]


class Command(BaseCommand):
    def handle(self, *args, **options):
        cms_pages = SlugPage.objects.all()
        existing_slug_serializers = {
            get_slug_page_serializer(cms_page): cms_page
            for cms_page in cms_pages
        }

        for serializer in CSM_SERIALIZERS:
            if serializer not in existing_slug_serializers:
                new_cms_page = serializer(data=serializer().fake_data())
                new_cms_page.is_valid()
                new_cms_page.save()
