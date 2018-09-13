from datetime import date

from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect

from officers.indexers import CRNewTimelineEventIndexer, CRNewTimelineEventPartialIndexer
from officers.doc_types import OfficerNewTimelineEventDocType
from officers.index_aliases import officers_index_alias
from data.factories import (
    OfficerFactory, OfficerAllegationFactory, AllegationFactory, OfficerHistoryFactory,
    SalaryFactory, VictimFactory, AttachmentFileFactory
)


class CRNewTimelineIndexerTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None

    def extract_data(self):
        indexer = CRNewTimelineEventIndexer()
        return [indexer.extract_datum(obj) for obj in indexer.get_queryset()]

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
        OfficerAllegationFactory()

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
        OfficerHistoryFactory(
            officer=officer,
            effective_date=None,
            end_date=None)
        OfficerHistoryFactory()

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
        SalaryFactory(
            officer=officer,
            spp_date=None
        )
        SalaryFactory()

        VictimFactory(
            allegation=allegation,
            race='White',
            age=34,
            gender='M')
        VictimFactory(
            allegation=allegation,
            race='Black',
            age=20,
            gender='F')
        VictimFactory()

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
        AttachmentFileFactory()

        rows = self.extract_data()
        expect(rows).to.have.length(5)
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
                },
                {
                    'race': 'Black',
                    'age': 20,
                    'gender': 'Female'
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


class CRNewTimelineEventPartialIndexerTestCase(TestCase):
    def test_get_queryset(self):
        allegation_123 = AllegationFactory(id=1212, crid='123')
        allegation_456 = AllegationFactory(id=2323, crid='456')
        OfficerAllegationFactory(allegation=allegation_123)
        OfficerAllegationFactory(allegation=allegation_123)
        OfficerAllegationFactory(allegation=allegation_456)

        indexer = CRNewTimelineEventPartialIndexer(updating_keys=['123'])
        result = list(indexer.get_queryset())
        expect([obj.allegation_id for obj in result]).to.eq([1212, 1212])
        expect(result[0].officer_id).to.ne(result[1].officer_id)

    def test_get_batch_queryset(self):
        allegation_123 = AllegationFactory(id=123, crid='123')
        allegation_456 = AllegationFactory(id=456, crid='456')
        OfficerAllegationFactory(allegation=allegation_123)
        OfficerAllegationFactory(allegation=allegation_123)
        OfficerAllegationFactory(allegation=allegation_456)

        result = CRNewTimelineEventPartialIndexer().get_batch_queryset(keys=['123'])
        expect([obj.allegation_id for obj in result]).to.eq([123, 123])
        expect(result[0].officer_id).to.ne(result[1].officer_id)

    def test_get_batch_update_docs_queries(self):
        officers_index_alias.read_index.delete(ignore=404)
        officers_index_alias.read_index.create(ignore=400)
        OfficerNewTimelineEventDocType.init(index=officers_index_alias.read_index._name)
        OfficerNewTimelineEventDocType(meta={'id': '1'}, **{
            'crid': '123456',
            'kind': 'CR',
        }).save()

        OfficerNewTimelineEventDocType(meta={'id': '2'}, **{
            'crid': '789',
            'kind': 'CR',
        }).save()

        OfficerNewTimelineEventDocType(meta={'id': '3'}, **{
            'crid': '789123',
            'kind': 'CR',
        }).save()
        officers_index_alias.read_index.refresh()

        update_docs_queries = CRNewTimelineEventPartialIndexer().get_batch_update_docs_queries(
            keys=['123456', '789', '432']
        )

        expect(set(update_docs_query.crid for update_docs_query in update_docs_queries)).to.eq({
            '123456', '789',
        })
