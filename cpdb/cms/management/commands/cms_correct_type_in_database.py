from django.core.management.base import BaseCommand

from cms.serializers import get_slug_page_serializer
from cms.models import SlugPage


class Command(BaseCommand):
    def handle(self, *args, **options):
        for slug_page in SlugPage.objects.all():
            serializer_class = get_slug_page_serializer(slug_page)
            serializer = serializer_class(
                slug_page,
                data=serializer_class().to_representation(slug_page, use_fake=True))
            serializer.is_valid()
            serializer.save()
