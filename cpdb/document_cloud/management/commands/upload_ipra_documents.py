from django.core.management.base import BaseCommand
from django.conf import settings
from documentcloud import DocumentCloud

from data.constants import AttachmentSourceType
from data.models import AttachmentFile


class Command(BaseCommand):
    help = 'Upload ipra documents to documentcloud'

    def handle(self, *args, **options):
        client = DocumentCloud(settings.DOCUMENTCLOUD_USER, settings.DOCUMENTCLOUD_PASSWORD)
        missing_documentcloud_docs = AttachmentFile.objects.filter(
            source_type=AttachmentSourceType.COPA,
            file_type='document'
        ).exclude(
            url__icontains='documentcloud'
        )
        for doc in missing_documentcloud_docs:
            new_doc = client.documents.upload(pdf=doc.original_url, title=doc.title, access='organization')
            doc.url = new_doc.canonical_url
            doc.save()
