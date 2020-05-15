from datetime import datetime, date

from django.test import TestCase

from robber import expect
import pytz

from officers.indexers import OfficerCoaccusalsIndexer
from data.factories import AllegationFactory, OfficerFactory, OfficerAllegationFactory


class OfficerCoaccusalsIndexerTestCase(TestCase):
    def extract_data(self):
        indexer = OfficerCoaccusalsIndexer()
        return [indexer.extract_datum(obj) for obj in indexer.get_queryset()]

    def test_extract_datum(self):
        officer1 = OfficerFactory(appointed_date=date(2001, 1, 1))
        officer2 = OfficerFactory(
            first_name='Officer',
            last_name='456',
            race='White',
            gender='M',
            birth_year=1950,
            rank='Police Officer',
            appointed_date=date(2002, 1, 1),
            civilian_allegation_percentile=11.1111,
            internal_allegation_percentile=22.2222,
            trr_percentile=33.3333,
            complaint_percentile=44.4444,
        )
        officer3 = OfficerFactory(
            first_name='Officer',
            last_name='789',
            race='Black',
            gender='M',
            birth_year=1970,
            rank='Po As Detective',
            appointed_date=date(2003, 1, 1),
            civilian_allegation_percentile=55.5555,
            internal_allegation_percentile=66.6666,
            trr_percentile=77.7777,
            complaint_percentile=88.8888,
        )

        allegation1 = AllegationFactory(incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc))
        allegation2 = AllegationFactory(incident_date=datetime(2003, 1, 1, tzinfo=pytz.utc))
        allegation3 = AllegationFactory(incident_date=datetime(2004, 1, 1, tzinfo=pytz.utc))
        allegation4 = AllegationFactory(incident_date=datetime(2005, 1, 1, tzinfo=pytz.utc))

        OfficerAllegationFactory(
            officer=officer2, allegation=allegation1, final_finding='SU', start_date=date(2003, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer3, allegation=allegation2, final_finding='SU', start_date=date(2004, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer3, allegation=allegation3, final_finding='NS', start_date=date(2005, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer1, allegation=allegation4, final_finding='NS', start_date=date(2006, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer2, allegation=allegation4, final_finding='NS', start_date=date(2006, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer3, allegation=allegation4, final_finding='NS', start_date=date(2006, 1, 1)
        )
        OfficerAllegationFactory(
            officer=officer1, allegation=allegation3, final_finding='NS', start_date=date(2006, 1, 1)
        )

        rows = self.extract_data()
        expect(rows).to.have.length(3)
        row = [obj for obj in rows if obj['id'] == officer1.id][0]

        expect(row).to.eq({
            'id': officer1.id,
            'coaccusals': [{
                'id': officer3.id,
                'full_name': 'Officer 789',
                'allegation_count': 3,
                'sustained_count': 1,
                'race': 'Black',
                'gender': 'Male',
                'birth_year': 1970,
                'coaccusal_count': 2,
                'rank': 'Po As Detective',
                'percentile_allegation': 88.8888,
                'percentile_allegation_civilian': 55.5555,
                'percentile_allegation_internal': 66.6666,
                'percentile_trr': 77.7777,
            }, {
                'id': officer2.id,
                'full_name': 'Officer 456',
                'allegation_count': 2,
                'sustained_count': 1,

                'race': 'White',
                'gender': 'Male',
                'birth_year': 1950,
                'coaccusal_count': 1,
                'rank': 'Police Officer',
                'percentile_allegation': 44.4444,
                'percentile_allegation_civilian': 11.1111,
                'percentile_allegation_internal': 22.2222,
                'percentile_trr': 33.3333,
            }]
        })

    def test_empty_coaccusal(self):
        OfficerFactory(id=3232)
        rows = self.extract_data()
        expect(rows).to.have.length(1)
        expect(rows[0]).to.eq({
            'id': 3232,
            'coaccusals': []
        })
