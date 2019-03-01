from tqdm import tqdm

from django.conf import settings

from documentcloud import DocumentCloud

from data.constants import AttachmentSourceType, MEDIA_TYPE_VIDEO, MEDIA_TYPE_DOCUMENT
from data.models import AttachmentFile, Allegation
from data_importer.ipra_crawler.portal_crawler import (
    OpenIpraInvestigationCrawler,
    ComplaintCrawler,
    VimeoSimpleAPI
)
from data_importer.ipra_crawler.parser import (
    Just,
    DateTimeField,
    CharField,
    CompositeField,
    ArraySourceField,
    PortalAttachmentFileField,
    SummaryReportsAttachmentFileField,
    SimpleField,
)
from data_importer.ipra_crawler.summary_reports_crawler import (
    OpenIpraSummaryReportsCrawler,
    OpenIpraYearSummaryReportsCrawler
)
from document_cloud.utils import parse_id, parse_link, get_url, format_copa_documentcloud_title
from shared.attachment_importer import BaseAttachmentImporter


def _get_chicagocopa_external_id(copa_url):
    return copa_url[copa_url.rindex('/') + 1:] if '/' in copa_url else copa_url


class IpraBaseAttachmentImporter(BaseAttachmentImporter):
    documentcloud_source_type = None

    def crawl_ipra(self):
        raise NotImplementedError

    @staticmethod
    def get_or_update_allegation(allegation_dict):
        crid = allegation_dict['crid']
        try:
            allegation = Allegation.objects.get(crid=crid)
        except Allegation.DoesNotExist:
            return None

        subjects = allegation_dict.get('subjects')
        if subjects:
            subjects = [subject for subject in subjects if subject and subject.lower() != 'unknown']
            if set(allegation.subjects) != set(subjects):
                allegation.subjects = subjects
                allegation.save()
        return allegation

    def update_attachments(self, allegation, attachment_dicts):
        created_attachments = []
        num_updated = 0

        for attachment_dict in attachment_dicts:
            chicagocopa_external_id = _get_chicagocopa_external_id(attachment_dict['original_url'])
            try:
                attachment = AttachmentFile.objects.get(
                    source_type__in=['', self.documentcloud_source_type],
                    allegation=allegation,
                    original_url__endswith=chicagocopa_external_id
                )
                created = False
            except AttachmentFile.DoesNotExist:
                attachment, created = AttachmentFile.objects.get_or_create(
                    source_type=self.source_type,
                    external_id=chicagocopa_external_id,
                    allegation=allegation,
                    defaults=attachment_dict
                )

            attachment_dict['preview_image_url'] = None
            if attachment_dict['file_type'] == MEDIA_TYPE_VIDEO and 'vimeo.com' in attachment_dict['original_url']:
                vimeo_data = VimeoSimpleAPI(chicagocopa_external_id).crawl()
                if vimeo_data is not None:
                    attachment_dict['preview_image_url'] = vimeo_data['thumbnail_small']
            if created:
                self.log_info(f'crid {allegation.crid} {attachment.original_url}')
                created_attachments.append(attachment)
            else:
                if attachment.source_type == self.documentcloud_source_type:
                    updating_fields = ['title', 'original_url', 'external_last_updated']
                    attachment_dict['title'] = format_copa_documentcloud_title(
                        allegation.crid, attachment_dict['title'], attachment.source_type
                    )
                else:
                    updating_fields = [
                        'file_type', 'title', 'url', 'original_url',
                        'external_last_updated', 'source_type', 'preview_image_url'
                    ]

                updated = False
                for field in updating_fields:
                    new_field_value = attachment_dict.get(field)
                    if new_field_value and getattr(attachment, field) != new_field_value:
                        setattr(attachment, field, new_field_value)
                        updated = True
                if updated:
                    attachment.save()
                    num_updated += 1
        return created_attachments, num_updated

    def update_allegation(self, incidents):
        for incident in incidents:
            allegation = self.get_or_update_allegation(incident['allegation'])
            if allegation is not None:
                yield (incident, allegation)

    def update_attachments_for_all_incidents(self, incidents):
        allegation_incidents = self.update_allegation(incidents)
        self.new_attachments = []
        self.num_updated_attachments = 0

        self.log_info('Import attachments process is about to start...')
        self.log_info(f'New {self.source_type.lower()} attachments found:')
        for incident, allegation in tqdm(allegation_incidents):
            created_attachments, num_updated = self.update_attachments(
                allegation,
                incident['allegation']['attachment_files']
            )
            self.new_attachments += created_attachments
            self.num_updated_attachments += num_updated

    def upload_to_documentcloud(self):
        client = DocumentCloud(settings.DOCUMENTCLOUD_USER, settings.DOCUMENTCLOUD_PASSWORD)

        attachments = AttachmentFile.objects.filter(
            source_type=self.source_type,
            file_type=MEDIA_TYPE_DOCUMENT
        )

        self.log_info(f'Uploading {len(attachments)} documents to DocumentCloud')

        for attachment in tqdm(attachments):
            source_type = AttachmentSourceType.SOURCE_TYPE_MAPPINGS[attachment.source_type]

            cloud_document = client.documents.upload(
                attachment.original_url,
                title=format_copa_documentcloud_title(attachment.allegation.crid, attachment.title,
                                                      attachment.source_type),
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

        self.log_info(f'Done uploading!')

    def crawl_and_update_attachments(self):
        try:
            self.set_current_step('CRAWLING')
            incidents = self.crawl_ipra()
            self.set_current_step('UPDATING ATTACHMENTS')
            self.update_attachments_for_all_incidents(incidents)
            self.set_current_step('UPLOADING TO DOCUMENTCLOUD')
            self.upload_to_documentcloud()
            self.set_current_step('RECORDING CRAWLER RESULT')
            self.record_success_crawler_result()
        except Exception:
            self.record_failed_crawler_result()
            return []
        return self.new_attachments


class IpraPortalAttachmentImporter(IpraBaseAttachmentImporter):
    source_type = AttachmentSourceType.PORTAL_COPA
    documentcloud_source_type = AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD
    all_source_types = [
        AttachmentSourceType.PORTAL_COPA,
        AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD
    ]

    def crawl_ipra(self):
        self.log_info('Crawling process is about to start...')
        links = OpenIpraInvestigationCrawler().crawl()
        self.log_info(f'Complaint crawler is starting! {len(links)} is ready to be crawled')
        raw_incidents = []

        for link in tqdm(links):
            raw_incidents.append(ComplaintCrawler(link).crawl())

        self.log_info(f'Parsed {len(raw_incidents)} crawled incidents')
        self.log_info('Done crawling!')

        return self.parse_incidents(raw_incidents)

    def parse_incidents(self, raw_incidents):
        schema = CompositeField(layout={
            'allegation': CompositeField(layout={
                'crid': CharField(field_name='log_number'),
                'incident_date': DateTimeField(field_name='time'),
                'attachment_files': ArraySourceField(field_name='attachments', parser=PortalAttachmentFileField()),
                'subjects': ArraySourceField(field_name='subjects', parser=SimpleField())
            }),
            'allegation_category': CompositeField(layout={
                'category': Just('Incident'),
                'allegation_name': CharField(field_name='type')
            }),
            'police_shooting': Just(True),
        })

        return [schema.parse(incident) for incident in raw_incidents]


class IpraSummaryReportsAttachmentImporter(IpraBaseAttachmentImporter):
    source_type = AttachmentSourceType.SUMMARY_REPORTS_COPA
    documentcloud_source_type = AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD
    all_source_types = [
        AttachmentSourceType.SUMMARY_REPORTS_COPA,
        AttachmentSourceType.SUMMARY_REPORTS_COPA_DOCUMENTCLOUD
    ]

    def crawl_ipra(self):
        self.log_info('Crawling process is about to start...')
        links = OpenIpraSummaryReportsCrawler().crawl()
        raw_incidents = []

        for link in tqdm(links):
            self.log_info(f'Crawling {link}')
            incidents_per_year = OpenIpraYearSummaryReportsCrawler(link).crawl()
            raw_incidents += incidents_per_year
            self.log_info(f'Parsed {len(incidents_per_year)} crawled incidents')

        self.log_info(f'Total crawled incidents: {len(raw_incidents)}')
        self.log_info('Done crawling!')
        return self.parse_incidents(raw_incidents)

    def parse_incidents(self, raw_incidents):
        schema = CompositeField(layout={
            'allegation': CompositeField(layout={
                'crid': CharField(field_name='log_num'),
                'attachment_files': ArraySourceField(
                    field_name='attachments',
                    parser=SummaryReportsAttachmentFileField()
                ),
            })
        })

        return [schema.parse(incident) for incident in raw_incidents]
