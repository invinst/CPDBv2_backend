import logging

from django.core.exceptions import ObjectDoesNotExist

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


logger = logging.getLogger('ipra_portal_crawler')


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
        logger.warn('Crawling process is about to start...')
        links = OpenIpraInvestigationCrawler().crawl()
        logger.warn('Complaint crawler is starting! {num_links} is ready to be crawled'.format(num_links=len(links)))
        incidents = []

        for link in links:
            logger.warn('Crawling {link}'.format(link=link))
            incidents.append(ComplaintCrawler(link).crawl())

        return incidents

    @staticmethod
    def import_allegation_and_attachments(incidents):
        for incident in incidents:
            crid = incident['allegation']['crid']
            logger.warn('Importing allegation with crid: {crid}'.format(crid=crid))

            try:
                allegation = Allegation.objects.get(crid=crid)

                subjects = [subject for subject in incident['allegation']['subjects']
                            if subject and subject.lower() != 'unknown']
                if set(allegation.subjects) != set(subjects):
                    allegation.subjects = subjects
                    allegation.save()

                for attachment in incident['allegation']['attachment_files']:
                    attachment['allegation'] = allegation
                    AttachmentFile.objects.get_or_create(
                        original_url=attachment['original_url'],
                        allegation=allegation,
                        defaults=attachment
                    )
            except ObjectDoesNotExist:
                pass

    @staticmethod
    def import_new():
        records = AutoOpenIPRA.crawl_open_ipra()
        logger.warn('Done crawling!')
        incidents = AutoOpenIPRA.parse_incidents(records)
        logger.warn('Parsed {num_incidents} crawled incidents'.format(num_incidents=len(incidents)))
        incidents = AutoOpenIPRA.fill_category(incidents)
        AutoOpenIPRA.import_allegation_and_attachments(incidents)
