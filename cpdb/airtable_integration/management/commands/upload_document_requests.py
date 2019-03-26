from django.core.management.base import BaseCommand

from airtable_integration.services.document_request_service import (
    CRRequestAirTableUploader,
    TRRRequestAirTableUploader
)


class Command(BaseCommand):
    help = 'Upload new document requests into FOIA airtable'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            dest='all',
            help='Update all AirTable rows',
        )

    def handle(self, *args, **options):
        CRRequestAirTableUploader.upload(options['all'])
        TRRRequestAirTableUploader.upload(options['all'])
