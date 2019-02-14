import logging

from tqdm import tqdm

from data.constants import AttachmentSourceType, MEDIA_TYPE_VIDEO
from data.models import AttachmentFile, Allegation, AllegationCategory
from data_importer.ipra_crawler.portal_crawler import (
    OpenIpraInvestigationCrawler,
    ComplaintCrawler,
    VimeoSimpleAPI
)
from data_importer.ipra_portal_crawler.parser import (
    Just,
    DateTimeField,
    CharField,
    CompositeField,
    ArraySourceField,
    AttachmentFileField,
    SimpleField
)
from document_cloud.models import DocumentCrawler
from document_cloud.utils import format_copa_documentcloud_title

_logger = logging.getLogger(__name__)


def _get_chicagocopa_external_id(copa_url):
    return copa_url[copa_url.rindex('/') + 1:] if '/' in copa_url else copa_url


def parse_incidents(incidents):
    schema = CompositeField(layout={
        'allegation': CompositeField(layout={
            'crid': CharField(field_name='log_number'),
            'incident_date': DateTimeField(field_name='time'),
            'attachment_files': ArraySourceField(field_name='attachments', parser=AttachmentFileField()),
            'subjects': ArraySourceField(field_name='subjects', parser=SimpleField())
        }),
        'allegation_category': CompositeField(layout={
            'category': Just('Incident'),
            'allegation_name': CharField(field_name='type')
        }),
        'police_shooting': Just(True),
    })

    return [schema.parse(incident) for incident in incidents]


def fill_category(incidents):
    for incident in incidents:
        if incident['allegation_category']['allegation_name']:
            allegation_category = AllegationCategory.objects.get(**incident['allegation_category'])
        else:
            allegation_category = None

        incident['allegation_category'] = allegation_category
    return incidents


def crawl_open_ipra(logger=_logger):
    logger.info('Crawling process is about to start...')
    links = OpenIpraInvestigationCrawler().crawl()
    logger.info(f'Complaint crawler is starting! {len(links)} is ready to be crawled')
    incidents = []

    for link in tqdm(links):
        incidents.append(ComplaintCrawler(link).crawl())

    return incidents


def get_or_update_allegation(allegation_dict):
    crid = allegation_dict['crid']
    try:
        allegation = Allegation.objects.get(crid=crid)
    except Allegation.DoesNotExist:
        return None

    subjects = [subject for subject in allegation_dict['subjects'] if subject and subject.lower() != 'unknown']
    if set(allegation.subjects) != set(subjects):
        allegation.subjects = subjects
        allegation.save()
    return allegation


def update_attachments(allegation, attachment_dicts):
    created_attachments = []
    num_updated = 0
    for attachment_dict in attachment_dicts:
        chicagocopa_external_id = _get_chicagocopa_external_id(attachment_dict['original_url'])
        try:
            attachment = AttachmentFile.objects.get(
                source_type__in=['', AttachmentSourceType.COPA_DOCUMENTCLOUD],
                allegation=allegation,
                original_url__endswith=chicagocopa_external_id
            )
            created = False
        except AttachmentFile.DoesNotExist:
            attachment, created = AttachmentFile.objects.get_or_create(
                source_type=AttachmentSourceType.COPA,
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
            if attachment.source_type == AttachmentSourceType.COPA_DOCUMENTCLOUD:
                updating_fields = ['title', 'original_url', 'external_last_updated']
                attachment_dict['title'] = format_copa_documentcloud_title(
                    allegation.crid, attachment_dict['title']
                )
            else:
                updating_fields = [
                    'file_type', 'title', 'url', 'original_url',
                    'external_last_updated', 'source_type', 'preview_image_url'
                ]

            updated = False
            for field in updating_fields:
                if getattr(attachment, field) != attachment_dict[field]:
                    setattr(attachment, field, attachment_dict[field])
                    updated = True
            if updated:
                attachment.save()
                num_updated += 1
    return created_attachments, num_updated


def update_allegation(incidents):
    for incident in incidents:
        allegation = get_or_update_allegation(incident['allegation'])
        if allegation is not None:
            yield (incident, allegation)


def update_attachments_for_all_incidents(allegation_incidents):
    new_attachments = []
    num_updated_attachments = 0

    for incident, allegation in tqdm(allegation_incidents):
        created_attachments, num_updated = update_attachments(
            allegation,
            incident['allegation']['attachment_files']
        )
        new_attachments += created_attachments
        num_updated_attachments += num_updated

    return new_attachments, num_updated_attachments


def record_crawler_result(new_attachments, num_updated_attachments, logger=_logger):
    num_documents = AttachmentFile.objects.filter(
        source_type__in=[AttachmentSourceType.COPA, AttachmentSourceType.COPA_DOCUMENTCLOUD]
    ).count()
    num_new_attachments = len(new_attachments)

    DocumentCrawler.objects.create(
        source_type=AttachmentSourceType.COPA,
        num_documents=num_documents,
        num_new_documents=num_new_attachments,
        num_updated_documents=num_updated_attachments
    )
    logger.info(
        f'Done importing! {num_new_attachments} created, '
        f'{num_updated_attachments} updated in {num_documents} copa attachments'
    )


def crawl_and_update_attachments(logger=_logger):
    records = crawl_open_ipra(logger)
    logger.info('Done crawling!')
    incidents = parse_incidents(records)
    logger.info(f'Parsed {len(incidents)} crawled incidents')
    incidents = fill_category(incidents)
    allegation_incidents = update_allegation(incidents)
    new_attachments, num_updated_attachments = update_attachments_for_all_incidents(allegation_incidents)
    record_crawler_result(new_attachments, num_updated_attachments, logger)
    return new_attachments
