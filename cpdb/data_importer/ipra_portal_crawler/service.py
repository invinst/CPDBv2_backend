import logging

from data.constants import AttachmentSourceType
from data.models import AttachmentFile, Allegation, AllegationCategory
from data_importer.ipra_portal_crawler.crawler import OpenIpraInvestigationCrawler, ComplaintCrawler
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

logger = logging.getLogger('django.command')


class AutoOpenIPRA(object):
    @staticmethod
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

    @staticmethod
    def fill_category(incidents):
        for incident in incidents:
            if incident['allegation_category']['allegation_name']:
                allegation_category = AllegationCategory.objects.get(**incident['allegation_category'])
            else:
                allegation_category = None

            incident['allegation_category'] = allegation_category
        return incidents

    @staticmethod
    def crawl_open_ipra():
        logger.info('Crawling process is about to start...')
        links = OpenIpraInvestigationCrawler().crawl()
        logger.info(f'Complaint crawler is starting! {len(links)} is ready to be crawled')
        incidents = []

        for link in links:
            logger.info(f'Crawling {link}')
            incidents.append(ComplaintCrawler(link).crawl())

        return incidents

    @staticmethod
    def get_or_update_allegation(allegation_dict):
        crid = allegation_dict['crid']
        logger.info(f'Importing allegation with crid: {crid}')
        try:
            allegation = Allegation.objects.get(crid=crid)
        except Allegation.DoesNotExist:
            return None

        subjects = [subject for subject in allegation_dict['subjects'] if subject and subject.lower() != 'unknown']
        if set(allegation.subjects) != set(subjects):
            allegation.subjects = subjects
            allegation.save()
        return allegation

    @staticmethod
    def update_attachments(allegation, attachment_dicts):
        num_created = num_updated = 0
        for attachment_dict in attachment_dicts:
            attachment_dict['allegation'] = allegation

            try:
                attachment = AttachmentFile.objects.get(
                    external_id=attachment_dict['original_url'],
                    source_type=AttachmentSourceType.COPA,
                    allegation=allegation
                )
                created = False
            except AttachmentFile.DoesNotExist:
                attachment, created = AttachmentFile.objects.get_or_create(
                    external_id=attachment_dict['original_url'],
                    source_type='',
                    allegation=allegation,
                    defaults=attachment_dict
                )

            if created:
                num_created += 1
            else:
                updating_fields = [
                    'file_type', 'title', 'url', 'original_url', 'tag', 'external_last_updated', 'source_type'
                ]
                updated = False
                for field in updating_fields:
                    if getattr(attachment, field) != attachment_dict[field]:
                        setattr(attachment, field, attachment_dict[field])
                        attachment.save()
                        updated = True
                if updated:
                    num_updated += 1
        return num_created, num_updated

    @staticmethod
    def import_allegation_and_attachments(incidents):
        num_new_attachments = num_updated_attachments = 0

        for incident in incidents:
            allegation = AutoOpenIPRA.get_or_update_allegation(incident['allegation'])
            if allegation:
                num_created, num_updated = AutoOpenIPRA.update_attachments(
                    allegation,
                    incident['allegation']['attachment_files']
                )
                num_new_attachments += num_created
                num_updated_attachments += num_updated

        num_documents = AttachmentFile.objects.filter(source_type=AttachmentSourceType.COPA).count()
        DocumentCrawler.objects.create(
            source_type=AttachmentSourceType.COPA,
            num_documents=num_documents,
            num_new_documents=num_new_attachments,
            num_updated_documents=num_updated_attachments
        )
        logger.info(
            f'Done importing! {num_new_attachments} created, {num_updated_attachments} updated '
            f'in {num_documents} copa attachments'
        )

    @staticmethod
    def import_new():
        records = AutoOpenIPRA.crawl_open_ipra()
        logger.info('Done crawling!')
        incidents = AutoOpenIPRA.parse_incidents(records)
        logger.info(f'Parsed {len(incidents)} crawled incidents')
        incidents = AutoOpenIPRA.fill_category(incidents)
        AutoOpenIPRA.import_allegation_and_attachments(incidents)
