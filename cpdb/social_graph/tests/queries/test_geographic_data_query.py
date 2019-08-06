from datetime import datetime

from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect
import pytz

from data.factories import AllegationFactory, OfficerFactory, OfficerAllegationFactory, AllegationCategoryFactory, \
    VictimFactory
from social_graph.queries.geographic_data_query import GeographyDataQuery
from trr.factories import TRRFactory


class GeographyDataQueryTestCase(TestCase):
    def test_cr_data(self):
        officer_1 = OfficerFactory(
            id=1,
            first_name='Jerome',
            last_name='Finnigan',
            allegation_count=20,
            sustained_count=10,
            birth_year=1980,
            race='Asian',
            gender='M',
            rank='Police Officer',
            resignation_date=datetime(2000, 1, 1, tzinfo=pytz.utc),
            trr_percentile=80,
            complaint_percentile=85,
            civilian_allegation_percentile=90,
            internal_allegation_percentile=95

        )
        officer_2 = OfficerFactory(
            id=2,
            first_name='Edward',
            last_name='May',
            allegation_count=10,
            sustained_count=5,
            birth_year=1970,
            race='Black',
            gender='M',
            rank='Police Officer',
            resignation_date=datetime(2000, 1, 1, tzinfo=pytz.utc),
            trr_percentile=50,
            complaint_percentile=55,
            civilian_allegation_percentile=60,
            internal_allegation_percentile=65

        )
        officer_3 = OfficerFactory(id=3)
        officer_4 = OfficerFactory(id=4)
        officers = [officer_1, officer_2, officer_3, officer_4]

        category_1 = AllegationCategoryFactory(category='Use of Force', allegation_name='Subcategory 1')
        category_2 = AllegationCategoryFactory(category='Illegal Search', allegation_name='Subcategory 2')
        allegation_1 = AllegationFactory(
            crid='123',
            most_common_category=category_1,
            coaccused_count=15,
            incident_date=datetime(2002, 1, 1, tzinfo=pytz.utc),
            point=Point(-35.5, 68.9),
            old_complaint_address='34XX Douglas Blvd',
        )
        allegation_2 = AllegationFactory(
            crid='456',
            most_common_category=category_2,
            coaccused_count=20,
            incident_date=datetime(2003, 1, 1, tzinfo=pytz.utc),
            point=Point(37.3, 86.2),
            old_complaint_address='34XX Douglas Blvd',
        )
        VictimFactory(
            gender='M',
            race='Black',
            age=35,
            allegation=allegation_1
        )
        VictimFactory(
            gender='F',
            race='White',
            age=40,
            allegation=allegation_2
        )
        OfficerAllegationFactory(
            officer=officer_1,
            allegation=allegation_1,
            recc_outcome='Separation',
            final_outcome='30 Day Suspension',
            final_finding='UN',
            allegation_category=category_1,
            disciplined=True
        )
        OfficerAllegationFactory(
            officer=officer_1,
            allegation=allegation_2,
            recc_outcome='Separation',
            final_outcome='28 Day Suspension',
            final_finding='UN',
            allegation_category=category_2,
            disciplined=True
        )
        OfficerAllegationFactory(
            officer=officer_2,
            allegation=allegation_2,
            recc_outcome='Separation',
            final_outcome='Suspended Over 30 Days',
            final_finding='SU',
            allegation_category=category_2,
            disciplined=True
        )

        expected_data = [allegation_1.crid, allegation_2.crid]
        results = list(GeographyDataQuery(officers).cr_data())
        results = sorted(item.crid for item in results)
        expect(results).to.eq(expected_data)

    def test_trr_data(self):
        officer_1 = OfficerFactory(
            id=1,
            first_name='Jerome',
            last_name='Finnigan',
            allegation_count=20,
            trr_percentile=80,
            complaint_percentile=85,
            civilian_allegation_percentile=90,
            internal_allegation_percentile=95

        )
        officer_2 = OfficerFactory(
            id=2,
            first_name='Edward',
            last_name='May',
            allegation_count=10,
            trr_percentile=50,
            complaint_percentile=55,
            civilian_allegation_percentile=60,
            internal_allegation_percentile=65

        )
        officer_3 = OfficerFactory(
            id=3,
            first_name='Jon',
            last_name='Snow',
            allegation_count=20,
            trr_percentile=80,
            complaint_percentile=85,
            civilian_allegation_percentile=90,
            internal_allegation_percentile=95

        )
        officer_4 = OfficerFactory(
            id=4,
            first_name='David',
            last_name='May',
            allegation_count=20,
            trr_percentile=80,
            complaint_percentile=85,
            civilian_allegation_percentile=90,
            internal_allegation_percentile=95

        )
        officers = [officer_1, officer_2, officer_3, officer_4]

        trr_1 = TRRFactory(
            id=1,
            officer=officer_3,
            trr_datetime=datetime(2004, 1, 1, tzinfo=pytz.utc),
            point=Point(-32.5, 61.3),
            taser=True,
            firearm_used=False,
            block='17XX',
            street='Division St',
        )
        trr_2 = TRRFactory(
            id=2,
            officer=officer_4,
            trr_datetime=datetime(2005, 1, 1, tzinfo=pytz.utc),
            point=Point(33.3, 78.4),
            taser=False,
            firearm_used=True,
            block='34XX',
            street='Douglas Blvd',
        )

        expected_data = [trr_1.id, trr_2.id]
        results = list(GeographyDataQuery(officers).trr_data())
        results = sorted(item.id for item in results)
        expect(results).to.eq(expected_data)
