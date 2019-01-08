from django.core.management import BaseCommand

from data_importer.ipra_portal_crawler.service import AutoOpenIPRA
from document_cloud.services.upload import upload_copa_documents


class Command(BaseCommand):
    def handle(self, *args, **options):
        AutoOpenIPRA.import_new()
        upload_copa_documents()
