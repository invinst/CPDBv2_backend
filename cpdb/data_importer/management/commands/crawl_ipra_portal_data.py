from django.core.management import BaseCommand

from data_importer.ipra_portal_crawler.service import AutoOpenIPRA
from document_cloud.services.upload import upload_copa_documents
from email_service.service import send_cr_attachment_available_email


class Command(BaseCommand):
    def handle(self, *args, **options):
        new_attachments = AutoOpenIPRA.import_new()
        upload_copa_documents()
        send_cr_attachment_available_email(new_attachments)
