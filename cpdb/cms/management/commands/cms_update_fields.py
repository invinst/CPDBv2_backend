from django.core.management.base import BaseCommand

from cms.serializers import get_slug_page_serializer
from cms.models import SlugPage


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('pages', nargs='*')

    def handle(self, *args, **options):
        pages = options['pages']
        slug_pages = SlugPage.objects.filter(slug__in=pages) if pages else SlugPage.objects.all()

        for slug_page in slug_pages:
            serializer_class = get_slug_page_serializer(slug_page)
            initial_data = serializer_class().to_representation(slug_page, use_fake=True)
            initial_fields = serializer_class().to_internal_value(initial_data)['fields']

            kept_fields = {
                key: value for key, value in slug_page.fields.items() if key in initial_fields
            }

            slug_page.fields = {**initial_fields, **kept_fields}
            slug_page.save()
