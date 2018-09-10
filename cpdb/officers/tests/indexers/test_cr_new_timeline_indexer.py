from datetime import date

from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect

from officers.indexers import CRNewTimelineEventIndexer
from data.factories import (
    OfficerFactory, OfficerAllegationFactory, AllegationFactory, OfficerHistoryFactory,
    SalaryFactory, VictimFactory, AttachmentFileFactory
)


class CRNewTimelineIndexerTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None

    def extract_data(self):
        indexer = CRNewTimelineEventIndexer()
        return [indexer.extract_datum(obj) for obj in indexer.get_query()]

    def test_regular_data(self):
        officer = OfficerFactory(id=123123)
        allegation = AllegationFactory(
            crid='123456',
            point=Point(35.5, 68.9))
        OfficerAllegationFactory(
            officer=officer,
            allegation=allegation,
            start_date=date(2012, 1, 1),
            allegation_category__category='Illegal Search',
            allegation_category__allegation_name='Search of premise/vehicle without warrant',
            final_finding='UN',
            final_outcome='Unknown'
        )
        OfficerAllegationFactory.create_batch(3, allegation=allegation)

        OfficerHistoryFactory(
            officer=officer,
            effective_date=date(2010, 1, 2),
            end_date=date(2010, 12, 31))
        OfficerHistoryFactory(
            officer=officer,
            effective_date=date(2011, 1, 1),
            end_date=date(2013, 1, 1),
            unit__unit_name='001',
            unit__description='District 1')
        OfficerHistoryFactory(
            officer=officer,
            effective_date=date(2013, 1, 2),
            end_date=date(2014, 1, 1))

        SalaryFactory(
            officer=officer,
            rank='Intern',
            spp_date=date(2010, 1, 1)
        )
        SalaryFactory(
            officer=officer,
            rank='Police Officer',
            spp_date=date(2011, 1, 1)
        )
        SalaryFactory(
            officer=officer,
            rank='Detective',
            spp_date=date(2014, 1, 1)
        )

        VictimFactory(
            allegation=allegation,
            race='White',
            age=34,
            gender='M')

        AttachmentFileFactory(
            allegation=allegation,
            file_type='document',
            title='CR document 1',
            url='http://foo.com/1',
            preview_image_url='http://web.com/image1'
        )
        AttachmentFileFactory(
            allegation=allegation,
            file_type='document',
            title='CR document 2',
            url='http://foo.com/2',
            preview_image_url='http://web.com/image2'
        )
        
        rows = self.extract_data()
        expect(rows).to.have.length(4)
        expect(rows[0]).to.eq({
            'officer_id': 123123,
            'date_sort': date(2012, 1, 1),
            'priority_sort': 30,
            'date': '2012-01-01',
            'kind': 'CR',
            'crid': '123456',
            'category': 'Illegal Search',
            'subcategory': 'Search of premise/vehicle without warrant',
            'finding': 'Unfounded',
            'outcome': 'Unknown',
            'coaccused': 4,
            'unit_name': '001',
            'unit_description': 'District 1',
            'rank': 'Police Officer',
            'victims': [
                {
                    'race': 'White',
                    'age': 34,
                    'gender': 'Male',
                }
            ],
            'point': {
                'lon': 35.5,
                'lat': 68.9
            },
            'attachments': [
                {
                    'title': 'CR document 1',
                    'url': 'http://foo.com/1',
                    'preview_image_url': 'http://web.com/image1',
                    'file_type': 'document',
                },
                {
                    'title': 'CR document 2',
                    'url': 'http://foo.com/2',
                    'preview_image_url': 'http://web.com/image2',
                    'file_type': 'document',
                },
            ]
        })
