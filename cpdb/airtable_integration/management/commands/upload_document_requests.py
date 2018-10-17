from django.core.management.base import BaseCommand

from airtable_integration.services.document_request_service import (
    CRRequestAirTableUploader,
    TRRRequestAirTableUploader
)


class Command(BaseCommand):
    help = 'Upload new document requests into FOIA airtable'

    def handle(self, *args, **options):
        CRRequestAirTableUploader.upload()
        TRRRequestAirTableUploader.upload()
