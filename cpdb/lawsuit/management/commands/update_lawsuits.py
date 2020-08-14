import logging

from django.core.management.base import BaseCommand

from lawsuit.importers import LawsuitImporter

logger = logging.getLogger('crawler.update_lawsuits')


class Command(BaseCommand):
    help = 'Update lawsuits info'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            help='Force update all lawsuits',
        )

    def handle(self, *args, **options):
        LawsuitImporter(
            logger,
            force_update=options['force']
        ).update_data()
