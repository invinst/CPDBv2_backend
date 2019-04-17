import pytz
from datetime import datetime

from django.test.testcases import TestCase

from robber.expect import expect

from data.factories import AllegationFactory, OfficerFactory, OfficerAllegationFactory
from pinboard.factories import PinboardFactory
from trr.factories import TRRFactory


class PinboardTestCase(TestCase):
    def test_all_officers(self):
        officer_1 = OfficerFactory(id=8562, first_name='Jerome', last_name='Finnigan')
        officer_2 = OfficerFactory(id=8563, first_name='Edward', last_name='May')
        officer_3 = OfficerFactory(id=8564, first_name='Joe', last_name='Parker')
        officer_4 = OfficerFactory(id=8565, first_name='Jane', last_name='Marry')
        officer_5 = OfficerFactory(id=8566, first_name='John', last_name='Parker')
        officer_6 = OfficerFactory(id=8567, first_name='William', last_name='People')
        officer_7 = OfficerFactory(id=8568, first_name='Zin', last_name='Flagg')

        allegation_1 = AllegationFactory(
            crid='123',
            is_officer_complaint=False,
            incident_date=datetime(2005, 12, 31, tzinfo=pytz.utc)
        )
        allegation_2 = AllegationFactory(
            crid='456',
            is_officer_complaint=True,
            incident_date=datetime(2006, 12, 31, tzinfo=pytz.utc)
        )
        allegation_3 = AllegationFactory(
            crid='789',
            is_officer_complaint=False,
            incident_date=datetime(2007, 12, 31, tzinfo=pytz.utc)
        )
        trr_1 = TRRFactory(
            id=1,
            officer=officer_6,
            trr_datetime=datetime(2008, 12, 31, tzinfo=pytz.utc)
        )
        trr_2 = TRRFactory(
            id=2,
            officer=officer_7,
            trr_datetime=datetime(2009, 12, 31, tzinfo=pytz.utc)
        )

        OfficerAllegationFactory(id=1, officer=officer_3, allegation=allegation_1)
        OfficerAllegationFactory(id=2, officer=officer_4, allegation=allegation_2)
        OfficerAllegationFactory(id=3, officer=officer_2, allegation=allegation_2)
        OfficerAllegationFactory(id=4, officer=officer_5, allegation=allegation_3)

        pinboard = PinboardFactory(
            description='abc',
        )

        pinboard.officers.set([officer_1, officer_2])
        pinboard.allegations.set([allegation_1, allegation_2])
        pinboard.trrs.set([trr_1, trr_2])

        expected_all_officers = [
            officer_2, officer_4, officer_1, officer_3, officer_6, officer_7
        ]

        expect(list(pinboard.all_officers)).to.eq(expected_all_officers)
