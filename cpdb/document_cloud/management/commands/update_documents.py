import re
from collections import OrderedDict

from django.core.management.base import BaseCommand
from django.conf import settings
from documentcloud import DocumentCloud

from data.models import AttachmentFile, Allegation
from data.constants import MEDIA_TYPE_DOCUMENT
from document_cloud.constants import AUTO_UPLOAD_DESCRIPTION
from document_cloud.services.documentcloud_service import DocumentcloudService
from document_cloud.models import DocumentCrawler, DocumentCloudSearchQuery
from cr.indexers import CRPartialIndexer
from officers.indexers import CRNewTimelineEventPartialIndexer


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

        try:
            # update if current info is mismatched
            updated_attachment = AttachmentFile.objects.get(allegation=allegation, external_id=documentcloud_id)
            updated = self.update_mismatched_existing_data(updated_attachment, cloud_document, document_type)
            return {'attachment': updated_attachment, 'is_new_attachment': False, 'updated': updated}

        except AttachmentFile.DoesNotExist:
            title = re.sub(r'([^\s])-([^\s])', '\g<1> \g<2>', cloud_document.title)
            additional_info = documentcloud_service.parse_link(cloud_document.canonical_url)

            new_attachment = AttachmentFile.objects.create(
                external_id=documentcloud_id,
                allegation=allegation,
                title=title,
                url=cloud_document.url,
                file_type=MEDIA_TYPE_DOCUMENT,
                tag=document_type,
                additional_info=additional_info,
                original_url=cloud_document.url,
                preview_image_url=cloud_document.normal_image_url,
                created_at=cloud_document.created_at,
                last_updated=cloud_document.updated_at
            )
            return {'attachment': new_attachment, 'is_new_attachment': True}

    def update_mismatched_existing_data(self, attachment, document, document_type):
        should_save = False
        mapping_fields = [
            ('url', 'url'),
            ('title', 'title'),
            ('preview_image_url', 'normal_image_url'),
            ('last_updated', 'updated_at'),
            ('created_at', 'created_at')
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
        client = DocumentCloud(settings.DOCUMENTCLOUD_USER, settings.DOCUMENTCLOUD_PASSWORD)

        kept_attachments = []
        changed_attachments = []
        num_new_attachments = 0
        num_updated_attachments = 0
        search_syntaxes = DocumentCloudSearchQuery.objects.all().values_list('type', 'query')
        for document_type, syntax in search_syntaxes:
            if syntax:
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
            url__icontains='documentcloud'
        ).exclude(id__in=all_attachment_ids)
        crids = set(attachment.allegation.crid for attachment in changed_attachments + list(deleted_attachments))
        deleted_attachments.delete()

        self.rebuild_related_elasticsearch_docs(crids=crids)

        num_documents = AttachmentFile.objects.filter(
            file_type=MEDIA_TYPE_DOCUMENT,
            url__icontains='documentcloud'
        ).count()
        DocumentCrawler.objects.create(
            num_documents=num_documents,
            num_new_documents=num_new_attachments,
            num_updated_documents=num_updated_attachments
        )
