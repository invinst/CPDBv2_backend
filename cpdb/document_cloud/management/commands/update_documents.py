import re
import logging
from collections import OrderedDict

from django.core.management.base import BaseCommand
from django.conf import settings
from documentcloud import DocumentCloud

from data.models import AttachmentFile, Allegation
from data.constants import MEDIA_TYPE_DOCUMENT, AttachmentSourceType
from document_cloud.constants import AUTO_UPLOAD_DESCRIPTION
from document_cloud.services.documentcloud_service import DocumentcloudService
from document_cloud.models import DocumentCrawler, DocumentCloudSearchQuery
from cr.indexers import CRPartialIndexer
from officers.indexers import CRNewTimelineEventPartialIndexer


logger = logging.getLogger('django.command')


def _get_url(document):
    document_url = document.canonical_url
    try:
        document_url = document.resources.pdf or document_url
    except AttributeError:
        pass
    return document_url


class Command(BaseCommand):
    help = 'Update complaint documents info'

    def process_documentcloud_document(self, cloud_document, document_type):
        documentcloud_service = DocumentcloudService()
        crid = documentcloud_service.parse_crid_from_title(cloud_document.title, document_type)
        if not crid:
            return
        try:
            allegation = Allegation.objects.get(crid=crid)
        except Allegation.DoesNotExist:
            return

        documentcloud_id = documentcloud_service.parse_id(cloud_document.id)
        if documentcloud_id is None:
            return

        setattr(cloud_document, 'url', _get_url(cloud_document))
        setattr(cloud_document, 'source_type', AttachmentSourceType.DOCUMENTCLOUD)

        try:
            try:
                updated_attachment = AttachmentFile.objects.get(
                    allegation=allegation, source_type=AttachmentSourceType.DOCUMENTCLOUD, external_id=documentcloud_id)
            except AttachmentFile.DoesNotExist:
                updated_attachment = AttachmentFile.objects.get(
                    allegation=allegation, source_type='', original_url=cloud_document.url)

            # update if current info is mismatched
            updated = self.update_mismatched_existing_data(updated_attachment, cloud_document, document_type)
            return {'attachment': updated_attachment, 'is_new_attachment': False, 'updated': updated}

        except AttachmentFile.DoesNotExist:
            title = re.sub(r'([^\s])-([^\s])', r'\g<1> \g<2>', cloud_document.title)
            additional_info = documentcloud_service.parse_link(cloud_document.canonical_url)

            logger.info('Updating documentcloud attachment url={url} with crid={crid}'.format(
                url=cloud_document.canonical_url,
                crid=crid
            ))
            new_attachment = AttachmentFile.objects.create(
                external_id=documentcloud_id,
                allegation=allegation,
                source_type=AttachmentSourceType.DOCUMENTCLOUD,
                title=title,
                url=cloud_document.url,
                file_type=MEDIA_TYPE_DOCUMENT,
                tag=document_type,
                additional_info=additional_info,
                original_url=cloud_document.url,
                preview_image_url=cloud_document.normal_image_url,
                external_created_at=cloud_document.created_at,
                external_last_updated=cloud_document.updated_at
            )
            return {'attachment': new_attachment, 'is_new_attachment': True}

    def update_mismatched_existing_data(self, attachment, document, document_type):
        should_save = False
        mapping_fields = [
            ('source_type', 'source_type'),
            ('url', 'url'),
            ('title', 'title'),
            ('preview_image_url', 'normal_image_url'),
            ('external_last_updated', 'updated_at'),
            ('external_created_at', 'created_at')
        ]

        for (model_field, doc_field) in mapping_fields:
            if getattr(attachment, model_field) != getattr(document, doc_field):
                setattr(attachment, model_field, getattr(document, doc_field))
                should_save = True
        if attachment.tag != document_type:
            attachment.tag = document_type
            should_save = True

        if should_save:
            try:
                logger.info('Updating documentcloud attachment url={url} with crid={crid}'.format(
                    url=attachment.original_url,
                    crid=attachment.allegation.crid
                ))
                attachment.save()
                return True
            except ValueError:
                return False

        return False

    def clean_documents(self, cloud_documents):
        if not cloud_documents:
            return []

        cleaned_results = OrderedDict()

        for cloud_document in cloud_documents:
            auto_uploaded = hasattr(cloud_document, 'description') and \
                            cloud_document.description == AUTO_UPLOAD_DESCRIPTION
            if not auto_uploaded and cloud_document.title not in cleaned_results:
                cleaned_results[cloud_document.title] = cloud_document

        return list(cleaned_results.values())

    def rebuild_related_elasticsearch_docs(self, crids):
        if not crids:
            return

        for indexer_klass in [CRPartialIndexer, CRNewTimelineEventPartialIndexer]:
            indexer = indexer_klass(updating_keys=crids)
            with indexer.index_alias.indexing():
                indexer.reindex()

    def handle(self, *args, **options):
        logger.info('Documentcloud crawling process is about to start...')
        client = DocumentCloud(settings.DOCUMENTCLOUD_USER, settings.DOCUMENTCLOUD_PASSWORD)

        kept_attachments = []
        changed_attachments = []
        num_new_attachments = 0
        num_updated_attachments = 0
        search_syntaxes = DocumentCloudSearchQuery.objects.all().values_list('type', 'query')
        for document_type, syntax in search_syntaxes:
            if syntax:
                logger.info('Searching Documentcloud for {syntax}'.format(syntax=syntax))
                documents = self.clean_documents(client.documents.search(syntax))
                for document in documents:
                    result = self.process_documentcloud_document(document, document_type)
                    if result:
                        attachment = result['attachment']

                        if result['is_new_attachment']:
                            changed_attachments.append(attachment)
                            num_new_attachments += 1
                        elif result['updated']:
                            changed_attachments.append(attachment)
                            num_updated_attachments += 1
                        else:
                            kept_attachments.append(attachment)

        all_attachment_ids = set(attachment.id for attachment in kept_attachments + changed_attachments)
        deleted_attachments = AttachmentFile.objects.filter(
            source_type=AttachmentSourceType.DOCUMENTCLOUD
        ).exclude(id__in=all_attachment_ids)
        crids = set(attachment.allegation.crid for attachment in changed_attachments + list(deleted_attachments))
        logger.info('Deleting {num} attachments'.format(num=deleted_attachments.count()))
        deleted_attachments.delete()

        self.rebuild_related_elasticsearch_docs(crids=crids)

        num_documents = AttachmentFile.objects.filter(
            file_type=MEDIA_TYPE_DOCUMENT,
            source_type=AttachmentSourceType.DOCUMENTCLOUD
        ).count()
        DocumentCrawler.objects.create(
            source_type=AttachmentSourceType.DOCUMENTCLOUD,
            num_documents=num_documents,
            num_new_documents=num_new_attachments,
            num_updated_documents=num_updated_attachments
        )
        logger.info('Done! {num_created} created, {num_updated} updated in {num} documentcloud attachments'.format(
            num_created=num_new_attachments,
            num_updated=num_updated_attachments,
            num=num_documents
        ))
