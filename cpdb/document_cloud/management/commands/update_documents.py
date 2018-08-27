import re
from collections import OrderedDict

from django.core.management.base import BaseCommand
from django.conf import settings
from documentcloud import DocumentCloud

from data.models import AttachmentFile, Allegation
from data.constants import MEDIA_TYPE_DOCUMENT
from document_cloud.services.documentcloud_service import DocumentcloudService
from document_cloud.models import DocumentCrawler, DocumentCloudSearchQuery
from cr.indexers import CRIndexer


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

        try:
            # update if current info is mismatched
            attachment = AttachmentFile.objects.get(allegation=allegation, url__icontains=cloud_document.id)
            self.update_mismatched_existing_data(attachment, cloud_document, document_type)
            return crid, attachment.id

        except AttachmentFile.DoesNotExist:
            title = re.sub(r'([^\s])-([^\s])', '\g<1> \g<2>', cloud_document.title)
            parsed_link = documentcloud_service.parse_link(cloud_document.canonical_url)
            attachment = AttachmentFile.objects.create(
                allegation=allegation,
                title=title,
                url=cloud_document.canonical_url,
                file_type=MEDIA_TYPE_DOCUMENT,
                tag=document_type,
                additional_info=parsed_link,
                original_url=cloud_document.canonical_url,
                preview_image_url=cloud_document.normal_image_url,
                created_at=cloud_document.created_at,
                last_updated=cloud_document.updated_at
            )
            return crid, attachment.id

    def update_mismatched_existing_data(self, attachment, document, document_type):
        should_save = False
        mapping_fields = [
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
            attachment.save()

    def clean_documents(self, cloud_documents):
        if not cloud_documents:
            return []

        cleaned_results = OrderedDict()

        for cloud_document in cloud_documents:
            if cloud_document.title not in cleaned_results:
                cleaned_results[cloud_document.title] = cloud_document

        return list(cleaned_results.values())

    def handle(self, *args, **options):
        client = DocumentCloud(settings.DOCUMENTCLOUD_USER, settings.DOCUMENTCLOUD_PASSWORD)

        crids = set()
        attachment_ids = []
        search_syntaxes = DocumentCloudSearchQuery.objects.all().values_list('type', 'query')
        for document_type, syntax in search_syntaxes:
            if syntax:
                documents = self.clean_documents(client.documents.search(syntax))
                for document in documents:
                    result = self.process_documentcloud_document(document, document_type)
                    if result:
                        crid, attachment_id = result
                        crids.add(crid)
                        attachment_ids.append(attachment_id)

        AttachmentFile.objects.filter(url__icontains='documentcloud').exclude(id__in=attachment_ids).delete()

        indexer = CRIndexer(queryset=Allegation.objects.filter(crid__in=crids))
        with indexer.index_alias.indexing():
            indexer.reindex()

        num_documents = AttachmentFile.objects.filter(
            file_type=MEDIA_TYPE_DOCUMENT,
            url__icontains='documentcloud'
        ).count()
        DocumentCrawler.objects.create(num_documents=num_documents)
