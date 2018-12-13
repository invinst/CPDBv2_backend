from django.core.management import BaseCommand

from data_importer.ipra_portal_crawler.service import AutoOpenIPRA
from document_cloud.services import upload_copa_documents
from email_service.service import send_attachment_available_notification


class Command(BaseCommand):
    def handle(self, *args, **options):
        new_attachments = AutoOpenIPRA.import_new()
        upload_copa_documents()
        send_attachment_available_notification(new_attachments)
