import re
import requests
import urllib3
from urllib.error import HTTPError

from django.db.models import Q
from django.conf import settings
from documentcloud import DocumentCloud

from tqdm import tqdm

from data.constants import AttachmentSourceType, MEDIA_TYPE_DOCUMENT
from data.models import AttachmentFile
from document_cloud.documentcloud_session import DocumentCloudSession
from document_cloud.utils import parse_link
from email_service.service import send_cr_attachment_available_email
from document_cloud.search import search_all
from shared.attachment_importer import BaseAttachmentImporter

BATCH_SIZE = 1000


class DocumentCloudAttachmentImporter(BaseAttachmentImporter):
    source_type = AttachmentSourceType.DOCUMENTCLOUD
    all_source_types = AttachmentSourceType.DOCUMENTCLOUD_SOURCE_TYPES

    def __init__(self, logger, force_update=False):
        super(DocumentCloudAttachmentImporter, self).__init__(logger)
        self.kept_attachments = []
        self.updated_attachments = []
        self.force_update = force_update
        self.client = DocumentCloud(settings.DOCUMENTCLOUD_USER, settings.DOCUMENTCLOUD_PASSWORD)

    mapping_fields = {
        'url': 'url',
        'title': 'title',
        'preview_image_url': 'normal_image_url',
        'external_last_updated': 'updated_at',
        'external_created_at': 'created_at',
        'tag': 'document_type',
        'source_type': 'source_type',
        'pages': 'pages',
    }

    @staticmethod
    def get_full_text(cloud_document):
        try:
            return re.sub(r'(\n *)+', '\n', cloud_document.full_text.decode('utf8')).strip()
        except (HTTPError, NotImplementedError):
            return ''

    @staticmethod
    def get_attachment(cloud_document):
        try:
            try:
                return AttachmentFile.objects.get(
                    Q(allegation=cloud_document.allegation,
                      source_type=cloud_document.source_type,
                      external_id=cloud_document.documentcloud_id) |
                    Q(allegation=cloud_document.allegation,
                      pending_documentcloud_id=cloud_document.documentcloud_id)
                )
            except AttachmentFile.DoesNotExist:
                return AttachmentFile.objects.get(
                    allegation=cloud_document.allegation,
                    source_type='',
                    original_url=cloud_document.url
                )
        except AttachmentFile.DoesNotExist:
            return

    def make_cloud_document_public(self, cloud_document):
        if cloud_document.access == 'public':
            return True
        elif cloud_document.access == 'private' or cloud_document.access == 'organization':
            cloud_document_access = cloud_document.access
            cloud_document.access = 'public'
            cloud_document.save()

            updated_cloud_document = self.client.documents.get(cloud_document.id)
            if updated_cloud_document.access == 'public':
                self.log_info(
                    f'Updated document {cloud_document.canonical_url} access from {cloud_document_access} to public'
                )
                return True
            else:
                self.log_info(
                    f'Can not update document {cloud_document.canonical_url} access '
                    f'from {cloud_document_access} to public'
                )
                return False
        elif (cloud_document.access == 'error' and
              cloud_document.source_type in AttachmentSourceType.COPA_DOCUMENTCLOUD_SOURCE_TYPES):
            return True
        else:
            self.log_info(f'Skip document {cloud_document.canonical_url} (access: {cloud_document.access})')
            return False

    def search_attachments(self):
        self.log_info('Documentcloud crawling process is about to start...')
        self.kept_attachments, self.new_attachments, self.updated_attachments = [], [], []

        self.log_info('New documentcloud attachments found:')
        for cloud_document in tqdm(search_all(self.logger), desc='Update documents'):
            if cloud_document.allegation and cloud_document.documentcloud_id and cloud_document.access != 'pending':
                if self.make_cloud_document_public(cloud_document):
                    attachment = self.get_attachment(cloud_document)
                    if attachment:
                        updated = self.update_attachment(attachment, cloud_document)
                        if updated:
                            self.updated_attachments.append(attachment)
                        else:
                            self.kept_attachments.append(attachment)
                    else:
                        self.log_info(f'crid {cloud_document.allegation.crid} {cloud_document.canonical_url}')
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
                        self.new_attachments.append(new_attachment)

        self.log_info('Done crawling!')

    def update_attachment(self, attachment, cloud_document):
        changed = self.force_update or bool(attachment.pending_documentcloud_id) or (
            not attachment.source_type or
            not attachment.external_last_updated or
            attachment.external_last_updated < cloud_document.updated_at
        )

        if changed:
            if attachment.pending_documentcloud_id and \
                attachment.pending_documentcloud_id == cloud_document.documentcloud_id and \
                    cloud_document.source_type in AttachmentSourceType.COPA_DOCUMENTCLOUD_SOURCE_TYPES:
                if cloud_document.access == 'error':
                    attachment.upload_fail_attempts += 1
                    cloud_document.delete()
                else:
                    attachment.source_type = AttachmentSourceType.SOURCE_TYPE_MAPPINGS[attachment.source_type]
                    attachment.external_id = attachment.pending_documentcloud_id
                    if attachment.manually_updated:
                        cloud_document.title = attachment.title
                        cloud_document.save()

                attachment.pending_documentcloud_id = None

            if cloud_document.access != 'error':
                if not attachment.manually_updated:
                    attachment.text_content = self.get_full_text(cloud_document)
                for model_field, doc_field in self.mapping_fields.items():
                    setattr(attachment, model_field, getattr(cloud_document, doc_field))

        return changed

    def update_attachments(self):
        all_attachment_ids = set(attachment.id for attachment in self.kept_attachments + self.updated_attachments)
        deleted_attachments = AttachmentFile.objects.filter(
            source_type=self.source_type
        ).exclude(id__in=all_attachment_ids)
        self.log_info(f'Deleting {deleted_attachments.count()} attachments')
        deleted_attachments.delete()

        self.num_updated_attachments = len(self.updated_attachments)
        self.log_info(f'Updating {self.num_updated_attachments} attachments')
        AttachmentFile.objects.bulk_update(
            self.updated_attachments,
            update_fields=[
                'external_id', 'title', 'tag', 'url', 'preview_image_url',
                'external_last_updated', 'external_created_at', 'text_content', 'source_type', 'pages',
                'pending_documentcloud_id', 'upload_fail_attempts'
            ],
            batch_size=BATCH_SIZE
        )
        for updated_attachment in self.updated_attachments:
            updated_attachment.update_allegation_summary()

        self.log_info(f'Creating {len(self.new_attachments)} attachments')
        AttachmentFile.objects.bulk_create(self.new_attachments)

    def upload_to_s3(self):
        for attachment in self.new_attachments + self.updated_attachments:
            attachment.upload_to_s3()

    def reprocess_text(self):
        try:
            with DocumentCloudSession(self.log_info) as session:
                session.request_reprocess_missing_text_documents()
        except (requests.exceptions.RequestException, urllib3.exceptions.HTTPError):
            pass

    def search_and_update_attachments(self):
        try:
            self.set_current_step('SEARCH ATTACHMENTS')
            self.search_attachments()
            self.set_current_step('UPDATING ATTACHMENTS')
            self.update_attachments()
            self.set_current_step('UPLOADING TO S3')
            self.upload_to_s3()
            self.set_current_step('REQUEST REPROCESS TEXT FOR NO ORC TEXT DOCUMENTS')
            self.reprocess_text()
            self.set_current_step('RECORDING CRAWLER RESULT')
            self.record_success_crawler_result()
            send_cr_attachment_available_email(self.new_attachments)
        except Exception:
            self.record_failed_crawler_result()
            return []
