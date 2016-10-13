from django.core.management.base import BaseCommand

from cms.cms_page_descriptors import get_all_descriptors


class Command(BaseCommand):
    def handle(self, *args, **options):
        for cms_page_descriptor in get_all_descriptors():
            cms_page_descriptor.seed_data()
