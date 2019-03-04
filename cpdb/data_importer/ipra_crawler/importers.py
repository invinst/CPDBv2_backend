from tqdm import tqdm

from data.constants import AttachmentSourceType, MEDIA_TYPE_VIDEO
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
from document_cloud.models import DocumentCrawler
from document_cloud.utils import format_copa_documentcloud_title


def _get_chicagocopa_external_id(copa_url):
    return copa_url[copa_url.rindex('/') + 1:] if '/' in copa_url else copa_url


class IpraBaseAttachmentImporter(object):
    source_type = None
    documentcloud_source_type = None

    def __init__(self, logger):
        self.logger = logger

    def crawl_ipra(self):
        raise NotImplementedError

    def parse_incidents(self, raw_incidents):
        raise NotImplementedError

    def log_info(self, message):
        self.logger.info(f'{self.source_type} - {message}')

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
        new_attachments = []
        num_updated_attachments = 0

        for incident, allegation in tqdm(allegation_incidents):
            created_attachments, num_updated = self.update_attachments(
                allegation,
                incident['allegation']['attachment_files']
            )
            new_attachments += created_attachments
            num_updated_attachments += num_updated

        return new_attachments, num_updated_attachments

    def record_crawler_result(self, new_attachments, num_updated_attachments):
        num_documents = AttachmentFile.objects.filter(
            source_type__in=[self.source_type, self.documentcloud_source_type]
        ).count()
        num_new_attachments = len(new_attachments)

        DocumentCrawler.objects.create(
            source_type=self.source_type,
            num_documents=num_documents,
            num_new_documents=num_new_attachments,
            num_updated_documents=num_updated_attachments
        )
        self.log_info(
            f'Done importing! {num_new_attachments} created, '
            f'{num_updated_attachments} updated in {num_documents} copa attachments'
        )

    def crawl_and_update_attachments(self):
        raw_incidents = self.crawl_ipra()
        self.log_info('Done crawling!')
        incidents = self.parse_incidents(raw_incidents)
        new_attachments, num_updated_attachments = self.update_attachments_for_all_incidents(incidents)
        self.record_crawler_result(new_attachments, num_updated_attachments)
        return new_attachments


class IpraPortalAttachmentImporter(IpraBaseAttachmentImporter):
    source_type = AttachmentSourceType.PORTAL_COPA
    documentcloud_source_type = AttachmentSourceType.PORTAL_COPA_DOCUMENTCLOUD

    def crawl_ipra(self):
        self.log_info('Crawling process is about to start...')
        links = OpenIpraInvestigationCrawler().crawl()
        self.log_info(f'Complaint crawler is starting! {len(links)} is ready to be crawled')
        raw_incidents = []

        for link in tqdm(links):
            raw_incidents.append(ComplaintCrawler(link).crawl())

        self.log_info(f'Parsed {len(raw_incidents)} crawled incidents')

        return raw_incidents

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

    def crawl_ipra(self):
        self.log_info('Crawling process is about to start...')
        links = OpenIpraSummaryReportsCrawler().crawl()
        self.log_info(f'Complaint crawler is starting! {len(links)} is ready to be crawled')
        raw_incidents = []

        for link in tqdm(links):
            raw_incidents += OpenIpraYearSummaryReportsCrawler(link).crawl()

        self.log_info(f'Parsed {len(raw_incidents)} crawled incidents')
        return raw_incidents

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
