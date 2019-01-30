from datetime import date, datetime

import pytz
from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect

from officers.indexers import TRRNewTimelineEventIndexer
from data.factories import OfficerFactory, OfficerHistoryFactory, SalaryFactory
from trr.factories import TRRFactory


class TRRNewTimelineEventIndexerTestCase(TestCase):
    def extract_data(self):
        indexer = TRRNewTimelineEventIndexer()
        return [indexer.extract_datum(obj) for obj in indexer.get_queryset()]

    def test_extract_datum(self):
        officer = OfficerFactory(id=123)
        OfficerHistoryFactory(
            officer=officer,
            effective_date=date(2009, 1, 1),
            end_date=date(2012, 1, 1),
            unit__unit_name='001',
            unit__description='District 1'
        )
        SalaryFactory(
            officer=officer,
            spp_date=date(2009, 1, 1),
            rank='Police Officer'
        )
        TRRFactory(
            id=2,
            officer=officer,
            trr_datetime=datetime(2010, 3, 4, tzinfo=pytz.utc),
            firearm_used=False,
            taser=False,
            point=Point(34.5, 67.8))

        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]).to.eq({
            'trr_id': 2,
            'officer_id': 123,
            'date_sort': date(2010, 3, 4),
            'priority_sort': 50,
            'date': '2010-03-04',
            'kind': 'FORCE',
            'taser': False,
            'firearm_used': False,
            'unit_name': '001',
            'unit_description': 'District 1',
            'rank': 'Police Officer',
            'point': {
                'lat': 67.8,
                'lon': 34.5
            },
        })

    def test_extract_datum_null_trr_datetime(self):
        TRRFactory(trr_datetime=None)
        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]['date_sort']).to.eq(None)
        expect(rows[0]['date']).to.eq(None)
