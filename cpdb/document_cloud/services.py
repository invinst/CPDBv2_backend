from documentcloud import DocumentCloud
from django.conf import settings

from document_cloud.utils import parse_id, parse_link
from data.constants import AttachmentSourceType, MEDIA_TYPE_DOCUMENT
from data.models import AttachmentFile
from cr.indexers import CRPartialIndexer
from officers.indexers import CRNewTimelineEventPartialIndexer


def rebuild_related_cr_indexes(attachments):
    crids = list(set([attachment.allegation.crid for attachment in attachments if attachment.allegation]))
    if crids:
        for indexer_klass in [CRPartialIndexer, CRNewTimelineEventPartialIndexer]:
            indexer = indexer_klass(updating_keys=crids)
            with indexer.index_alias.indexing():
                indexer.reindex()


def upload_documents_from_copa_source():
    client = DocumentCloud(settings.DOCUMENTCLOUD_USER, settings.DOCUMENTCLOUD_PASSWORD)

    attachments = AttachmentFile.objects.filter(source_type=AttachmentSourceType.COPA, file_type=MEDIA_TYPE_DOCUMENT)

    for attachment in attachments:
        cloud_document = client.documents.upload(attachment.original_url, f'CRID {attachment.allegation.crid} CR')
        attachment.external_id = parse_id(cloud_document.id)
        attachment.source_type = AttachmentSourceType.DOCUMENTCLOUD
        attachment.original_url = cloud_document.url
        attachment.url = cloud_document.url
        attachment.title = cloud_document.title
        attachment.preview_image_url = cloud_document.normal_image_url,
        attachment.created_at = cloud_document.created_at,
        attachment.last_updated = cloud_document.updated_at

        additional_info = parse_link(cloud_document.canonical_url)
        attachment.additional_info = additional_info

        attachment.save()

        rebuild_related_cr_indexes(attachments)
