from datetime import date

from django.test import TestCase

from robber import expect

from officers.indexers import RankChangeNewTimelineEventIndexer
from data.factories import SalaryFactory, OfficerFactory, OfficerHistoryFactory


class RankChangeNewTimelineEventIndexerTestCase(TestCase):
    def extract_data(self):
        indexer = RankChangeNewTimelineEventIndexer()
        return [indexer.extract_datum(obj) for obj in indexer.get_queryset()]

    def test_extract_datum(self):
        officer1 = OfficerFactory(id=123)
        officer2 = OfficerFactory(id=456)
        OfficerHistoryFactory(
            officer=officer1,
            effective_date=date(2006, 1, 1),
            unit__unit_name='001',
            unit__description='District 1')
        OfficerHistoryFactory(
            officer=officer1,
            effective_date=date(2008, 1, 1),
            unit__unit_name='002',
            unit__description='District 2')
        OfficerHistoryFactory(
            officer=officer2,
            effective_date=date(2004, 1, 1),
            unit__unit_name='003',
            unit__description='District 3')
        SalaryFactory(
            officer=officer1, salary=5000, year=2005, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer1, salary=10000, year=2006, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer1, salary=15000, year=2007, rank='Sergeant', spp_date=date(2007, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer2, salary=5000, year=2005, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer2, salary=15000, year=2006, rank='Detective', spp_date=date(2006, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer2, salary=20000, year=2007, rank='Detective', spp_date=date(2006, 1, 1),
            start_date=date(2005, 1, 1)
        )

        rows = self.extract_data()
        expect(rows).to.have.length(4)
        expect(rows).to.eq([
            {
                'officer_id': 123,
                'date_sort': date(2005, 1, 1),
                'priority_sort': 25,
                'date': '2005-01-01',
                'kind': 'RANK_CHANGE',
                'unit_name': '',
                'unit_description': '',
                'rank': 'Police Officer',
            },
            {
                'officer_id': 123,
                'date_sort': date(2007, 1, 1),
                'priority_sort': 25,
                'date': '2007-01-01',
                'kind': 'RANK_CHANGE',
                'unit_name': '001',
                'unit_description': 'District 1',
                'rank': 'Sergeant',
            },
            {
                'officer_id': 456,
                'date_sort': date(2005, 1, 1),
                'priority_sort': 25,
                'date': '2005-01-01',
                'kind': 'RANK_CHANGE',
                'unit_name': '003',
                'unit_description': 'District 3',
                'rank': 'Police Officer',
            },
            {
                'officer_id': 456,
                'date_sort': date(2006, 1, 1),
                'priority_sort': 25,
                'date': '2006-01-01',
                'kind': 'RANK_CHANGE',
                'unit_name': '003',
                'unit_description': 'District 3',
                'rank': 'Detective',
            }
        ])
