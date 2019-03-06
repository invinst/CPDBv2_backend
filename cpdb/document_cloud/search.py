import logging

from django.conf import settings
from documentcloud import DocumentCloud

from data.constants import AttachmentSourceType
from data.models import AttachmentFile, Allegation
from document_cloud.models import DocumentCloudSearchQuery
from document_cloud.utils import parse_id, get_url, parse_crid_from_title

_logger = logging.getLogger(__name__)


# We need to this filter because we have two attachments which have a same title
# One is updated by STAGING and one by PRODUCTION
def _remove_invalid_documents(cloud_documents):
    existing_copa_documentcloud_ids = AttachmentFile.objects.filter(
        source_type__in=AttachmentSourceType.COPA_DOCUMENTCLOUD_SOURCE_TYPES
    ).values_list('external_id', flat=True).distinct()

    def valid_document(cloud_document):
        return cloud_document.source_type not in AttachmentSourceType.COPA_DOCUMENTCLOUD_SOURCE_TYPES or \
               cloud_document.documentcloud_id in existing_copa_documentcloud_ids

    return filter(valid_document, cloud_documents)


def _remove_duplicated(cloud_documents):
    existing_documentcloud_ids = AttachmentFile.objects.filter(
        source_type=AttachmentSourceType.DOCUMENTCLOUD
    ).values_list('external_id', flat=True).distinct()

    copa_documents = []
    documentcloud_documents = []
    for document in cloud_documents:
        if document.source_type in AttachmentSourceType.COPA_DOCUMENTCLOUD_SOURCE_TYPES:
            copa_documents.append(document)
        else:
            documentcloud_documents.append(document)

    # After being sorted, all existing documents will be at the end of the list,
    # which means it will be kept after dict comprehending
    ordered_documentcloud_documents = sorted(
        documentcloud_documents,
        key=lambda d: d.documentcloud_id in existing_documentcloud_ids
    )
    cleaned_results = {cloud_document.title: cloud_document for cloud_document in ordered_documentcloud_documents}

    return copa_documents + list(cleaned_results.values())


def _add_attributes(cloud_documents, document_type):
    for cloud_document in cloud_documents:
        from_copa = hasattr(cloud_document, 'description') \
                    and cloud_document.description in AttachmentSourceType.COPA_DOCUMENTCLOUD_SOURCE_TYPES
        source_type = cloud_document.description if from_copa else AttachmentSourceType.DOCUMENTCLOUD
        setattr(cloud_document, 'source_type', source_type)

        setattr(cloud_document, 'url', get_url(cloud_document))
        setattr(cloud_document, 'documentcloud_id', parse_id(cloud_document.id))
        setattr(cloud_document, 'document_type', document_type)

        crid = parse_crid_from_title(cloud_document.title, document_type)
        allegation = Allegation.objects.filter(crid=crid).first()
        setattr(cloud_document, 'allegation', allegation)

    return cloud_documents


def search_all(logger=_logger):
    client = DocumentCloud(settings.DOCUMENTCLOUD_USER, settings.DOCUMENTCLOUD_PASSWORD)
    search_syntaxes = DocumentCloudSearchQuery.objects.all().values_list('type', 'query')
    all_documents = []
    for document_type, syntax in search_syntaxes:
        if syntax:
            logger.info(f'Searching Documentcloud for {syntax}')
            all_documents += _remove_duplicated(
                _remove_invalid_documents(
                    _add_attributes(client.documents.search(syntax), document_type)
                )
            )
    return all_documents
