from datetime import date

from django.test import TestCase

from robber import expect

from officers.indexers import UnitChangeNewTimelineEventIndexer
from data.factories import OfficerHistoryFactory, SalaryFactory, OfficerFactory


class UnitChangeNewTimelineEventIndexerTestCase(TestCase):
    def extract_data(self):
        indexer = UnitChangeNewTimelineEventIndexer()
        return [indexer.extract_datum(obj) for obj in indexer.get_queryset()]

    def test_extract_data(self):
        officer = OfficerFactory(id=2323)
        OfficerHistoryFactory(
            officer=officer,
            unit__unit_name='001',
            unit__description='District 1',
            effective_date=date(2002, 2, 3),
            end_date=date(2003, 3, 4),
        )

        SalaryFactory(
            officer=officer,
            rank='Intern',
            spp_date=date(2000, 1, 1)
        )
        SalaryFactory(
            officer=officer,
            rank='Police Officer',
            spp_date=date(2001, 1, 1)
        )
        SalaryFactory(
            officer=officer,
            rank='Detective',
            spp_date=date(2004, 1, 1)
        )
        SalaryFactory(
            officer=officer,
            spp_date=None
        )
        SalaryFactory()

        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]).to.eq({
            'officer_id': 2323,
            'date_sort': date(2002, 2, 3),
            'priority_sort': 20,
            'date': '2002-02-03',
            'kind': 'UNIT_CHANGE',
            'unit_name': '001',
            'unit_description': 'District 1',
            'rank': 'Police Officer',
        })
