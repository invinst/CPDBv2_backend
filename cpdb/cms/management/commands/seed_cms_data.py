from django.core.management.base import BaseCommand

from cms.cms_page_descriptors import get_all_slug_page_descriptors, get_all_id_page_descriptor_classes


class Command(BaseCommand):
    def handle(self, *args, **options):
        for descriptor in get_all_slug_page_descriptors():
            descriptor.seed_data()

        for descriptor_class in get_all_id_page_descriptor_classes():
            for _ in range(16):
                descriptor = descriptor_class()
                descriptor.seed_data()
