import logging

from django.core.management import BaseCommand
from django.conf import settings

from documentcloud import DocumentCloud
from tqdm import tqdm

from data_importer.ipra_crawler.importers import IpraPortalAttachmentImporter, IpraSummaryReportsAttachmentImporter
from email_service.service import send_cr_attachment_available_email
from data.constants import AttachmentSourceType, MEDIA_TYPE_DOCUMENT
from data.models import AttachmentFile
from document_cloud.utils import parse_id, parse_link, get_url, format_copa_documentcloud_title

logger = logging.getLogger('crawler.crawl_ipra_portal_data')


def upload_copa_documents():
    client = DocumentCloud(settings.DOCUMENTCLOUD_USER, settings.DOCUMENTCLOUD_PASSWORD)

    attachments = AttachmentFile.objects.filter(
        source_type__in=[AttachmentSourceType.PORTAL_COPA, AttachmentSourceType.SUMMARY_REPORTS_COPA],
        file_type=MEDIA_TYPE_DOCUMENT
    )

    logger.info(f'Uploading {len(attachments)} documents to DocumentCloud')

    for attachment in tqdm(attachments):
        source_type = AttachmentSourceType.SOURCE_TYPE_MAPPINGS[attachment.source_type]

        cloud_document = client.documents.upload(
            attachment.original_url,
            title=format_copa_documentcloud_title(attachment.allegation.crid, attachment.title),
            description=source_type,
            access='public',
            force_ocr=True
        )

        attachment.external_id = parse_id(cloud_document.id)
        attachment.source_type = source_type
        attachment.title = cloud_document.title
        attachment.url = get_url(cloud_document)
        attachment.tag = 'CR'
        attachment.additional_info = parse_link(cloud_document.canonical_url)
        attachment.preview_image_url = cloud_document.normal_image_url
        attachment.external_last_updated = cloud_document.updated_at
        attachment.external_created_at = cloud_document.created_at
        attachment.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        new_attachments = IpraPortalAttachmentImporter(logger).crawl_and_update_attachments()
        new_attachments += IpraSummaryReportsAttachmentImporter(logger).crawl_and_update_attachments()
        upload_copa_documents()
        send_cr_attachment_available_email(new_attachments)
