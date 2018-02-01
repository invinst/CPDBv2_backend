import re
from collections import OrderedDict

from django.core.management.base import BaseCommand
from django.conf import settings
from documentcloud import DocumentCloud

from data.models import AttachmentFile, Allegation
from data.constants import MEDIA_TYPE_DOCUMENT
from document_cloud.services.documentcloud_service import DocumentcloudService
from document_cloud.models import DocumentCrawler, DocumentCloudSearchQuery


class Command(BaseCommand):
    help = 'Update complaint documents info'

    def process_documentcloud_result(self, result, document_type):
        documentcloud_service = DocumentcloudService()
        crid = documentcloud_service.parse_crid_from_title(result.title, document_type)
        if not crid:
            return

        try:
            allegation = Allegation.objects.get(crid=crid)
        except Allegation.DoesNotExist:
            return

        try:
            # update if current info is mismatched
            document = AttachmentFile.objects.get(allegation=allegation, url__icontains=result.id)
            self.update_mismatched_existing_data(document, result)
        except AttachmentFile.DoesNotExist:
            title = re.sub(r'([^\s])-([^\s])', '\g<1> \g<2>', result.title)
            parsed_link = documentcloud_service.parse_link(result.canonical_url)
            AttachmentFile.objects.create(
                allegation=allegation,
                title=title,
                url=result.canonical_url,
                file_type=MEDIA_TYPE_DOCUMENT,
                tag=document_type,
                additional_info=parsed_link,
                original_url=result.canonical_url,
                preview_image_url=result.normal_image_url,
                last_updated=result.updated_at
            )

    def update_mismatched_existing_data(self, document, result):

        should_save = False
        # Normalize document title if document originate from documentcloud
        if document.title != result.title:
            document.title = result.title
            should_save = True
        if document.preview_image_url != result.normal_image_url:
            document.preview_image_url = result.normal_image_url
            should_save = True
        if document.last_updated != result.updated_at:
            document.last_updated = result.updated_at
            should_save = True

        if should_save:
            document.save()

    def clean_documentcloud_results(self, results):
        cleaned_results = OrderedDict()

        for result in results:
            if result.title not in cleaned_results:
                cleaned_results[result.title] = result

        return list(cleaned_results.values())

    def handle(self, *args, **options):
        client = DocumentCloud(settings.DOCUMENTCLOUD_USER, settings.DOCUMENTCLOUD_PASSWORD)

        search_syntaxes = DocumentCloudSearchQuery.objects.all().values_list('type', 'query')

        for document_type, syntax in search_syntaxes:
            if not syntax:
                continue

            results = client.documents.search(syntax)

            if results:
                results = self.clean_documentcloud_results(results)
                for result in results:
                    self.process_documentcloud_result(result, document_type)

        num_documents = AttachmentFile.objects.filter(
            file_type=MEDIA_TYPE_DOCUMENT,
            url__icontains='documentcloud'
        ).count()
        DocumentCrawler.objects.create(num_documents=num_documents)
