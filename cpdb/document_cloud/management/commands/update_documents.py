import logging
import re
from urllib.error import HTTPError

from django.core.management.base import BaseCommand

from tqdm import tqdm

from data.constants import AttachmentSourceType, MEDIA_TYPE_DOCUMENT
from data.models import AttachmentFile
from document_cloud.models import DocumentCrawler
from document_cloud.utils import parse_link
from email_service.service import send_cr_attachment_available_email
from document_cloud.search import search_all

logger = logging.getLogger('crawler.update_documents')

BATCH_SIZE = 1000


def get_attachment(cloud_document):
    try:
        try:
            return AttachmentFile.objects.get(
                allegation=cloud_document.allegation,
                source_type=cloud_document.source_type,
                external_id=cloud_document.documentcloud_id
            )
        except AttachmentFile.DoesNotExist:
            return AttachmentFile.objects.get(
                allegation=cloud_document.allegation,
                source_type='',
                original_url=cloud_document.url
            )
    except AttachmentFile.DoesNotExist:
        return


mapping_fields = {
    'url': 'url',
    'title': 'title',
    'preview_image_url': 'normal_image_url',
    'external_last_updated': 'updated_at',
    'external_created_at': 'created_at',
    'tag': 'document_type',
    'source_type': 'source_type',
}


def get_full_text(cloud_document):
    try:
        return re.sub(r'(\n *)+', '\n', cloud_document.full_text.decode('utf8')).strip()
    except (HTTPError, NotImplementedError):
        return ''


def update_attachment(attachment, cloud_document):
    changed = (
        not attachment.source_type or
        not attachment.external_last_updated or
        attachment.external_last_updated < cloud_document.updated_at
    )
    if changed:
        attachment.text_content = get_full_text(cloud_document)
        for model_field, doc_field in mapping_fields.items():
            setattr(attachment, model_field, getattr(cloud_document, doc_field))

    return changed


def save_attachments(kept_attachments, new_attachments, updated_attachments):
    all_attachment_ids = set(attachment.id for attachment in kept_attachments + updated_attachments)
    deleted_attachments = AttachmentFile.objects.filter(
        source_type=AttachmentSourceType.DOCUMENTCLOUD
    ).exclude(id__in=all_attachment_ids)
    logger.info(f'Deleting {deleted_attachments.count()} attachments')
    deleted_attachments.delete()

    num_updated_attachments = len(updated_attachments)
    logger.info(f'Updating {num_updated_attachments} attachments')
    AttachmentFile.objects.bulk_update(
        updated_attachments,
        update_fields=[
            'title', 'tag', 'url', 'preview_image_url',
            'external_last_updated', 'external_created_at', 'text_content', 'source_type'
        ],
        batch_size=BATCH_SIZE
    )

    num_new_attachments = len(new_attachments)
    logger.info(f'Creating {num_new_attachments} attachments')
    AttachmentFile.objects.bulk_create(new_attachments)

    log_changes(num_new_attachments, num_updated_attachments)


def log_changes(num_new_attachments, num_updated_attachments):
    num_documents = AttachmentFile.objects.filter(
        source_type__in=[
            AttachmentSourceType.DOCUMENTCLOUD,
            AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD,
            AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD
        ]
    ).count()
    DocumentCrawler.objects.create(
        source_type=AttachmentSourceType.DOCUMENTCLOUD,
        num_documents=num_documents,
        num_new_documents=num_new_attachments,
        num_updated_documents=num_updated_attachments
    )
    logger.info(
        f'Done! {num_new_attachments} created, {num_updated_attachments} updated '
        f'in {num_documents} documentcloud attachments'
    )


class Command(BaseCommand):
    help = 'Update complaint documents info'

    def handle(self, *args, **options):
        logger.info('Documentcloud crawling process is about to start...')
        kept_attachments, new_attachments, updated_attachments = [], [], []

        for cloud_document in tqdm(search_all(logger), desc='Update documents'):
            if cloud_document.allegation and cloud_document.documentcloud_id:
                attachment = get_attachment(cloud_document)
                if attachment:
                    updated = update_attachment(attachment, cloud_document)
                    if updated:
                        updated_attachments.append(attachment)
                    else:
                        kept_attachments.append(attachment)
                else:
                    logger.info(
                        'Creating documentcloud attachment '
                        f'url={cloud_document.canonical_url} '
                        f'crid={cloud_document.allegation.crid}'
                    )
                    new_attachment = AttachmentFile(
                        external_id=cloud_document.documentcloud_id,
                        allegation=cloud_document.allegation,
                        source_type=cloud_document.source_type,
                        title=cloud_document.title,
                        url=cloud_document.url,
                        file_type=MEDIA_TYPE_DOCUMENT,
                        tag=cloud_document.document_type,
                        additional_info=parse_link(cloud_document.canonical_url),
                        original_url=cloud_document.url,
                        preview_image_url=cloud_document.normal_image_url,
                        external_created_at=cloud_document.created_at,
                        external_last_updated=cloud_document.updated_at
                    )
                    new_attachments.append(new_attachment)
        save_attachments(kept_attachments, new_attachments, updated_attachments)
        for attachment in new_attachments + updated_attachments:
            attachment.upload_to_s3()

        send_cr_attachment_available_email(new_attachments)
