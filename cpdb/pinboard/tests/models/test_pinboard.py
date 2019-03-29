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

    def test_relevant_coaccusals(self):
        pinned_officer_1 = OfficerFactory(id=1)
        pinned_officer_2 = OfficerFactory(id=2)
        pinned_allegation_1 = AllegationFactory(crid='1')
        pinned_allegation_2 = AllegationFactory(crid='2')
        pinboard = PinboardFactory(
            title='Test pinboard',
            description='Test description',
            officers=[pinned_officer_1, pinned_officer_2],
            allegations=[pinned_allegation_1, pinned_allegation_2],
        )

        officer_coaccusal_11 = OfficerFactory(id=11)
        officer_coaccusal_21 = OfficerFactory(id=21)
        OfficerFactory(id=99)

        allegation_11 = AllegationFactory(crid='11')
        allegation_12 = AllegationFactory(crid='12')
        allegation_13 = AllegationFactory(crid='13')
        allegation_14 = AllegationFactory(crid='14')
        OfficerAllegationFactory(allegation=allegation_11, officer=pinned_officer_1)
        OfficerAllegationFactory(allegation=allegation_12, officer=pinned_officer_1)
        OfficerAllegationFactory(allegation=allegation_13, officer=pinned_officer_1)
        OfficerAllegationFactory(allegation=allegation_14, officer=pinned_officer_1)
        OfficerAllegationFactory(allegation=allegation_11, officer=officer_coaccusal_11)
        OfficerAllegationFactory(allegation=allegation_12, officer=officer_coaccusal_11)
        OfficerAllegationFactory(allegation=allegation_13, officer=officer_coaccusal_11)
        OfficerAllegationFactory(allegation=allegation_14, officer=officer_coaccusal_11)

        allegation_21 = AllegationFactory(crid='21')
        allegation_22 = AllegationFactory(crid='22')
        allegation_23 = AllegationFactory(crid='23')
        OfficerAllegationFactory(allegation=allegation_21, officer=pinned_officer_2)
        OfficerAllegationFactory(allegation=allegation_22, officer=pinned_officer_2)
        OfficerAllegationFactory(allegation=allegation_23, officer=pinned_officer_2)
        OfficerAllegationFactory(allegation=allegation_21, officer=officer_coaccusal_21)
        OfficerAllegationFactory(allegation=allegation_22, officer=officer_coaccusal_21)
        OfficerAllegationFactory(allegation=allegation_23, officer=officer_coaccusal_21)

        allegation_coaccusal_12 = OfficerFactory(id=12)
        allegation_coaccusal_22 = OfficerFactory(id=22)
        OfficerAllegationFactory(allegation=pinned_allegation_1, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_2, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_2, officer=allegation_coaccusal_22)

        relevant_coaccusals = pinboard.relevant_coaccusals
        expect(relevant_coaccusals).to.have.length(4)
        expect(relevant_coaccusals[0].id).to.eq(11)
        expect(relevant_coaccusals[1].id).to.eq(21)
        expect(relevant_coaccusals[2].id).to.eq(12)
        expect(relevant_coaccusals[3].id).to.eq(22)
