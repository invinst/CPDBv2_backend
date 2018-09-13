from datetime import date

from django.test import TestCase

from robber import expect

from officers.indexers import JoinedNewTimelineEventIndexer
from data.factories import SalaryFactory, OfficerFactory, OfficerHistoryFactory


class JoinedNewTimelineEventIndexerTestCase(TestCase):
    def extract_data(self):
        indexer = JoinedNewTimelineEventIndexer()
        return [indexer.extract_datum(obj) for obj in indexer.get_queryset()]

    def test_extract_datum(self):
        officer = OfficerFactory(id=123, appointed_date=date(2011, 1, 1))
        OfficerHistoryFactory(
            officer=officer,
            effective_date=date(2011, 1, 1),
            unit__unit_name='001',
            unit__description='District 1'
        )
        OfficerHistoryFactory(
            officer=officer,
            effective_date=date(2013, 1, 1),
            unit__unit_name='002',
            unit__description='District 2'
        )
        SalaryFactory(
            officer=officer, rank='Police Officer', spp_date=date(2011, 1, 1)
        )
        SalaryFactory(
            officer=officer, rank='Sergent', spp_date=date(2013, 1, 1)
        )
        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]).to.eq({
            'officer_id': 123,
            'date_sort': date(2011, 1, 1),
            'priority_sort': 10,
            'date': '2011-01-01',
            'kind': 'JOINED',
            'unit_name': '001',
            'unit_description': 'District 1',
            'rank': 'Police Officer',
        })

    def test_empty_unit(self):
        OfficerFactory(appointed_date=date(2005, 1, 1))
        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]['unit_name']).to.eq('')
        expect(rows[0]['unit_description']).to.eq('')
