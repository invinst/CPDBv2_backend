from datetime import datetime

from django.test.testcases import TestCase

import pytz
from robber.expect import expect

from data.factories import (
    AllegationFactory, OfficerFactory, OfficerAllegationFactory, InvestigatorAllegationFactory,
    PoliceWitnessFactory,
    AttachmentFileFactory,
)
from pinboard.factories import PinboardFactory, ExamplePinboardFactory
from trr.factories import TRRFactory


class PinboardTestCase(TestCase):
    def test_clone(self):
        officer_1 = OfficerFactory(id=1)
        officer_2 = OfficerFactory(id=2)

        allegation_1 = AllegationFactory(crid='123abc')
        allegation_2 = AllegationFactory(crid='456def')

        trr_1 = TRRFactory(id=1, officer=OfficerFactory(id=3))
        trr_2 = TRRFactory(id=2, officer=OfficerFactory(id=4))

        pinboard = PinboardFactory(
            title='Pinboard title',
            description='Pinboard title',
            officers=(officer_1, officer_2),
            allegations=(allegation_1, allegation_2),
            trrs=(trr_1, trr_2),
        )
        cloned_pinboard = pinboard.clone()
        cloned_pinboard.refresh_from_db()

        officers = set(pinboard.officers.all().values_list('id', flat=True))
        allegations = set(pinboard.allegations.all().values_list('crid', flat=True))
        trrs = set(pinboard.trrs.all().values_list('id', flat=True))

        cloned_officers = set(cloned_pinboard.officers.all().values_list('id', flat=True))
        cloned_allegations = set(cloned_pinboard.allegations.all().values_list('crid', flat=True))
        cloned_trrs = set(cloned_pinboard.trrs.all().values_list('id', flat=True))

        expect(pinboard.title).to.eq(cloned_pinboard.title)
        expect(pinboard.description).to.eq(cloned_pinboard.description)
        expect(officers).to.eq(cloned_officers)
        expect(allegations).to.eq(cloned_allegations)
        expect(trrs).to.eq(cloned_trrs)
        expect(cloned_pinboard.source_pinboard).to.eq(pinboard)

    def test_clone_duplicate(self):
        pinboard = PinboardFactory(
            title='Pinboard title',
            description='Pinboard title',
            officers=(),
            allegations=(),
            trrs=(),
        )
        cloned_pinboard = pinboard.clone(is_duplicated=True)
        expect(cloned_pinboard.title).to.eq('Pinboard title copy')

    def test_clone_duplicate_with_copy_in_title(self):
        pinboard = PinboardFactory(
            title='Pinboard title copy',
            description='Pinboard title',
            officers=(),
            allegations=(),
            trrs=(),
        )
        cloned_pinboard = pinboard.clone(is_duplicated=True)
        expect(cloned_pinboard.title).to.eq('Pinboard title copy 2')

    def test_clone_duplicate_with_copy_number_in_title(self):
        pinboard = PinboardFactory(
            title='Pinboard title copy 2',
            description='Pinboard title',
            officers=(),
            allegations=(),
            trrs=(),
        )
        cloned_pinboard = pinboard.clone(is_duplicated=True)
        expect(cloned_pinboard.title).to.eq('Pinboard title copy 3')

    def test_clone_duplicate_with_copy_copy_number_in_title(self):
        pinboard = PinboardFactory(
            title='Pinboard title copy copy',
            description='Pinboard title',
            officers=(),
            allegations=(),
            trrs=(),
        )
        cloned_pinboard = pinboard.clone(is_duplicated=True)
        expect(cloned_pinboard.title).to.eq('Pinboard title copy copy 2')

    def test_clone_duplicate_with_copy_number_in_middle_of_title(self):
        pinboard = PinboardFactory(
            title='Pinboard title copy 2d',
            description='Pinboard title',
            officers=(),
            allegations=(),
            trrs=(),
        )
        cloned_pinboard = pinboard.clone(is_duplicated=True)
        expect(cloned_pinboard.title).to.eq('Pinboard title copy 2d copy')

    def test_str(self):
        pinboard = PinboardFactory(
            id='abcd1234',
            title='Pinboard title',
        )

        pinboard_no_title = PinboardFactory(
            id='dcba4321',
            title='',
        )

        expect(str(pinboard)).to.eq('abcd1234 - Pinboard title')
        expect(str(pinboard_no_title)).to.eq('dcba4321')

    def test_is_empty(self):
        officer_1 = OfficerFactory(id=1)
        officer_2 = OfficerFactory(id=2)

        allegation_1 = AllegationFactory(crid='123abc')
        allegation_2 = AllegationFactory(crid='456def')

        trr_1 = TRRFactory(id=1, officer=OfficerFactory(id=3))
        trr_2 = TRRFactory(id=2, officer=OfficerFactory(id=4))

        pinboard_full = PinboardFactory(
            officers=(officer_1, officer_2),
            allegations=(allegation_1, allegation_2),
            trrs=(trr_1, trr_2),
        )

        pinboard_with_officers = PinboardFactory(
            officers=(officer_1, officer_2),
        )

        pinboard_with_allegations = PinboardFactory(
            allegations=(allegation_1, allegation_2),
        )

        pinboard_with_trrs = PinboardFactory(
            trrs=(trr_1, trr_2),
        )

        pinboard_empty = PinboardFactory()

        expect(pinboard_full.is_empty).to.be.false()
        expect(pinboard_with_officers.is_empty).to.be.false()
        expect(pinboard_with_allegations.is_empty).to.be.false()
        expect(pinboard_with_trrs.is_empty).to.be.false()
        expect(pinboard_empty.is_empty).to.be.true()

    def test_example_pinboards(self):
        officer_1 = OfficerFactory(id=1)
        officer_2 = OfficerFactory(id=2)

        allegation_1 = AllegationFactory(crid='123abc')
        allegation_2 = AllegationFactory(crid='456def')

        trr_1 = TRRFactory(id=1, officer=OfficerFactory(id=3))
        trr_2 = TRRFactory(id=2, officer=OfficerFactory(id=4))

        pinboard_full = PinboardFactory(
            officers=(officer_1, officer_2),
            allegations=(allegation_1, allegation_2),
            trrs=(trr_1, trr_2),
        )

        pinboard_with_officers = PinboardFactory(
            officers=(officer_1, officer_2),
        )

        pinboard_with_allegations = PinboardFactory(
            allegations=(allegation_1, allegation_2),
        )

        pinboard_with_trrs = PinboardFactory(
            trrs=(trr_1, trr_2),
        )

        pinboard_empty = PinboardFactory()

        e_pinboard_1 = PinboardFactory(
            title='Example pinboard 1',
            description='Example pinboard 1',
        )
        example_pinboard_1 = ExamplePinboardFactory(pinboard=e_pinboard_1)

        e_pinboard_2 = PinboardFactory(
            title='Example pinboard 1',
            description='Example pinboard 1',
        )
        example_pinboard_2 = ExamplePinboardFactory(pinboard=e_pinboard_2)

        expect(pinboard_empty.example_pinboards).to.have.length(2)
        expect(pinboard_empty.example_pinboards).to.contain(example_pinboard_1)
        expect(pinboard_empty.example_pinboards).to.contain(example_pinboard_2)

        expect(pinboard_with_officers.example_pinboards).to.be.none()
        expect(pinboard_with_allegations.example_pinboards).to.be.none()
        expect(pinboard_with_trrs.example_pinboards).to.be.none()
        expect(pinboard_full.example_pinboards).to.be.none()

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

        expected_all_officers = {officer_2, officer_4, officer_1, officer_3, officer_6, officer_7}
        expect(set(pinboard.all_officers)).to.eq(expected_all_officers)

    def test_all_officer_ids(self):
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

        expected_all_officer_ids = {officer_2.id, officer_4.id, officer_1.id, officer_3.id, officer_6.id, officer_7.id}
        expect(set(pinboard.all_officer_ids)).to.eq(expected_all_officer_ids)

    def test_officer_ids(self):
        pinned_officer_1 = OfficerFactory(id=1)
        pinned_officer_2 = OfficerFactory(id=2)
        pinboard = PinboardFactory(
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer_1, pinned_officer_2])
        expect(list(pinboard.officer_ids)).to.eq([1, 2])

    def test_crids(self):
        pinned_allegation_1 = AllegationFactory(crid='1')
        pinned_allegation_2 = AllegationFactory(crid='2')
        pinboard = PinboardFactory(
            title='Test pinboard',
            description='Test description',
        )
        pinboard.allegations.set([pinned_allegation_1, pinned_allegation_2])
        expect(list(pinboard.crids)).to.eq(['1', '2'])

    def test_trr_ids(self):
        pinned_trr_1 = TRRFactory(id=1)
        pinned_trr_2 = TRRFactory(id=2)
        pinboard = PinboardFactory(
            title='Test pinboard',
            description='Test description',
        )
        pinboard.trrs.set([pinned_trr_1, pinned_trr_2])
        expect(list(pinboard.trr_ids)).to.eq([1, 2])

    def test_relevant_coaccusals(self):
        pinned_officer_1 = OfficerFactory(id=1)
        pinned_officer_2 = OfficerFactory(id=2)
        pinned_allegation_1 = AllegationFactory(crid='1')
        pinned_allegation_2 = AllegationFactory(crid='2')
        pinned_trr = TRRFactory(officer__id=77)
        pinboard = PinboardFactory(
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer_1, pinned_officer_2])
        pinboard.allegations.set([pinned_allegation_1, pinned_allegation_2])
        pinboard.trrs.set([pinned_trr])
        not_relevant_allegation = AllegationFactory(crid='999')

        officer_coaccusal_11 = OfficerFactory(id=11)
        officer_coaccusal_21 = OfficerFactory(id=21)
        OfficerFactory(id=99, first_name='Not Relevant', last_name='Officer')

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
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=officer_coaccusal_11)

        allegation_21 = AllegationFactory(crid='21')
        allegation_22 = AllegationFactory(crid='22')
        allegation_23 = AllegationFactory(crid='23')
        OfficerAllegationFactory(allegation=allegation_21, officer=pinned_officer_2)
        OfficerAllegationFactory(allegation=allegation_22, officer=pinned_officer_2)
        OfficerAllegationFactory(allegation=allegation_23, officer=pinned_officer_2)
        OfficerAllegationFactory(allegation=allegation_21, officer=officer_coaccusal_21)
        OfficerAllegationFactory(allegation=allegation_22, officer=officer_coaccusal_21)
        OfficerAllegationFactory(allegation=allegation_23, officer=officer_coaccusal_21)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=officer_coaccusal_21)

        allegation_coaccusal_12 = OfficerFactory(id=12)
        allegation_coaccusal_22 = OfficerFactory(id=22)
        OfficerAllegationFactory(allegation=pinned_allegation_1, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_2, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_2, officer=allegation_coaccusal_22)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=allegation_coaccusal_22)

        relevant_coaccusals = list(pinboard.relevant_coaccusals)

        expect(relevant_coaccusals).to.have.length(5)
        expect(relevant_coaccusals[0].id).to.eq(11)
        expect(relevant_coaccusals[0].coaccusal_count).to.eq(4)
        expect(relevant_coaccusals[1].id).to.eq(21)
        expect(relevant_coaccusals[1].coaccusal_count).to.eq(3)
        expect(relevant_coaccusals[2].id).to.eq(12)
        expect(relevant_coaccusals[2].coaccusal_count).to.eq(2)
        expect({relevant_coaccusal.id for relevant_coaccusal in relevant_coaccusals[3:5]}).to.eq({22, 77})
        expect(relevant_coaccusals[3].coaccusal_count).to.eq(1)
        expect(relevant_coaccusals[4].coaccusal_count).to.eq(1)

    def test_relevant_complaints_coaccusal_count_via_trr(self):
        officer_coaccusal_11 = OfficerFactory(id=11)
        officer_coaccusal_21 = OfficerFactory(id=21)
        OfficerFactory(id=99, first_name='Not Relevant', last_name='Officer')

        pinned_officer_1 = OfficerFactory(id=1)
        pinned_officer_2 = OfficerFactory(id=2)
        pinned_allegation_1 = AllegationFactory(crid='1')
        pinned_allegation_2 = AllegationFactory(crid='2')
        pinned_trr_1 = TRRFactory(officer__id=77)
        pinned_trr_2 = TRRFactory(officer=officer_coaccusal_11)
        pinboard = PinboardFactory(
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer_1, pinned_officer_2])
        pinboard.allegations.set([pinned_allegation_1, pinned_allegation_2])
        pinboard.trrs.set([pinned_trr_1, pinned_trr_2])
        not_relevant_allegation = AllegationFactory(crid='999')

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
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=officer_coaccusal_11)

        allegation_21 = AllegationFactory(crid='21')
        allegation_22 = AllegationFactory(crid='22')
        allegation_23 = AllegationFactory(crid='23')
        OfficerAllegationFactory(allegation=allegation_21, officer=pinned_officer_2)
        OfficerAllegationFactory(allegation=allegation_22, officer=pinned_officer_2)
        OfficerAllegationFactory(allegation=allegation_23, officer=pinned_officer_2)
        OfficerAllegationFactory(allegation=allegation_21, officer=officer_coaccusal_21)
        OfficerAllegationFactory(allegation=allegation_22, officer=officer_coaccusal_21)
        OfficerAllegationFactory(allegation=allegation_23, officer=officer_coaccusal_21)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=officer_coaccusal_21)

        allegation_coaccusal_12 = OfficerFactory(id=12)
        allegation_coaccusal_22 = OfficerFactory(id=22)
        OfficerAllegationFactory(allegation=pinned_allegation_1, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_2, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=allegation_coaccusal_12)
        OfficerAllegationFactory(allegation=pinned_allegation_2, officer=allegation_coaccusal_22)
        OfficerAllegationFactory(allegation=not_relevant_allegation, officer=allegation_coaccusal_22)

        relevant_coaccusals = list(pinboard.relevant_coaccusals)

        expect(relevant_coaccusals).to.have.length(5)
        expect(relevant_coaccusals[0].id).to.eq(11)
        expect(relevant_coaccusals[0].coaccusal_count).to.eq(5)
        expect(relevant_coaccusals[1].id).to.eq(21)
        expect(relevant_coaccusals[1].coaccusal_count).to.eq(3)
        expect(relevant_coaccusals[2].id).to.eq(12)
        expect(relevant_coaccusals[2].coaccusal_count).to.eq(2)
        expect({relevant_coaccusal.id for relevant_coaccusal in relevant_coaccusals[3:5]}).to.eq({22, 77})
        expect(relevant_coaccusals[3].coaccusal_count).to.eq(1)
        expect(relevant_coaccusals[4].coaccusal_count).to.eq(1)

    def test_relevant_complaints_via_accused_officers(self):
        pinned_officer_1 = OfficerFactory(id=1)
        pinned_officer_2 = OfficerFactory(id=2)
        pinned_officer_3 = OfficerFactory(id=3)
        relevant_allegation_1 = AllegationFactory(crid='1', incident_date=datetime(2002, 2, 21, tzinfo=pytz.utc))
        relevant_allegation_2 = AllegationFactory(crid='2', incident_date=datetime(2002, 2, 22, tzinfo=pytz.utc))
        AllegationFactory(crid='not relevant')
        pinboard = PinboardFactory(
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer_1, pinned_officer_2, pinned_officer_3])
        OfficerAllegationFactory(officer=pinned_officer_1, allegation=relevant_allegation_1)
        OfficerAllegationFactory(officer=pinned_officer_2, allegation=relevant_allegation_2)

        relevant_complaints = list(pinboard.relevant_complaints)

        expect(relevant_complaints).to.have.length(2)
        expect(relevant_complaints[0].crid).to.eq('2')
        expect(relevant_complaints[1].crid).to.eq('1')

    def test_relevant_complaints_filter_out_pinned_allegations(self):
        pinned_officer_1 = OfficerFactory(id=1)
        pinned_officer_2 = OfficerFactory(id=2)
        pinned_allegation_1 = AllegationFactory(crid='1')
        pinned_allegation_2 = AllegationFactory(crid='2')
        pinboard = PinboardFactory(
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer_1, pinned_officer_2])
        pinboard.allegations.set([pinned_allegation_1, pinned_allegation_2])
        OfficerAllegationFactory(officer=pinned_officer_1, allegation=pinned_allegation_1)
        OfficerAllegationFactory(officer=pinned_officer_2, allegation=pinned_allegation_2)
        AllegationFactory(crid='not relevant')

        expect(list(pinboard.relevant_complaints)).to.have.length(0)

    def test_relevant_complaints_via_investigator(self):
        pinned_investigator_1 = OfficerFactory(id=1)
        pinned_investigator_2 = OfficerFactory(id=2)
        pinned_investigator_3 = OfficerFactory(id=3)
        not_relevant_officer = OfficerFactory(id=999)
        relevant_allegation_1 = AllegationFactory(crid='1', incident_date=datetime(2002, 2, 21, tzinfo=pytz.utc))
        relevant_allegation_2 = AllegationFactory(crid='2', incident_date=datetime(2002, 2, 22, tzinfo=pytz.utc))
        relevant_allegation_3 = AllegationFactory(crid='3', incident_date=datetime(2002, 2, 23, tzinfo=pytz.utc))
        not_relevant_allegation = AllegationFactory(crid='999')
        pinboard = PinboardFactory(
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_investigator_1, pinned_investigator_2, pinned_investigator_3])
        InvestigatorAllegationFactory(investigator__officer=pinned_investigator_1, allegation=relevant_allegation_1)
        InvestigatorAllegationFactory(investigator__officer=pinned_investigator_2, allegation=relevant_allegation_2)
        InvestigatorAllegationFactory(investigator__officer=pinned_investigator_3, allegation=relevant_allegation_3)
        InvestigatorAllegationFactory(investigator__officer=not_relevant_officer, allegation=not_relevant_allegation)

        relevant_complaints = list(pinboard.relevant_complaints)

        expect(relevant_complaints).to.have.length(3)
        expect(relevant_complaints[0].crid).to.eq('3')
        expect(relevant_complaints[1].crid).to.eq('2')
        expect(relevant_complaints[2].crid).to.eq('1')

    def test_relevant_complaints_via_police_witnesses(self):
        pinned_officer_1 = OfficerFactory(id=1)
        pinned_officer_2 = OfficerFactory(id=2)
        not_relevant_officer = OfficerFactory(id=999)
        relevant_allegation_11 = AllegationFactory(crid='11', incident_date=datetime(2002, 2, 21, tzinfo=pytz.utc))
        relevant_allegation_12 = AllegationFactory(crid='12', incident_date=datetime(2002, 2, 22, tzinfo=pytz.utc))
        relevant_allegation_21 = AllegationFactory(crid='21', incident_date=datetime(2002, 2, 23, tzinfo=pytz.utc))
        not_relevant_allegation = AllegationFactory(crid='999')
        pinboard = PinboardFactory(
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer_1, pinned_officer_2])
        PoliceWitnessFactory(allegation=relevant_allegation_11, officer=pinned_officer_1)
        PoliceWitnessFactory(allegation=relevant_allegation_12, officer=pinned_officer_1)
        PoliceWitnessFactory(allegation=relevant_allegation_21, officer=pinned_officer_2)
        PoliceWitnessFactory(allegation=not_relevant_allegation, officer=not_relevant_officer)

        relevant_complaints = list(pinboard.relevant_complaints)

        expect(relevant_complaints).to.have.length(3)
        expect(relevant_complaints[0].crid).to.eq('21')
        expect(relevant_complaints[1].crid).to.eq('12')
        expect(relevant_complaints[2].crid).to.eq('11')

    def test_relevant_complaints_order_officers(self):
        pinned_officer_1 = OfficerFactory(id=1, allegation_count=3)
        pinned_officer_2 = OfficerFactory(id=2)
        pinned_officer_3 = OfficerFactory(id=3)
        officer_4 = OfficerFactory(id=4, allegation_count=2)
        officer_5 = OfficerFactory(id=5, allegation_count=4)
        relevant_allegation_1 = AllegationFactory(crid='1', incident_date=datetime(2002, 2, 21, tzinfo=pytz.utc))
        relevant_allegation_2 = AllegationFactory(crid='2', incident_date=datetime(2002, 2, 22, tzinfo=pytz.utc))
        AllegationFactory(crid='not relevant')
        pinboard = PinboardFactory(
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer_1, pinned_officer_2, pinned_officer_3])
        OfficerAllegationFactory(officer=pinned_officer_1, allegation=relevant_allegation_1)
        OfficerAllegationFactory(officer=officer_4, allegation=relevant_allegation_1)
        OfficerAllegationFactory(officer=officer_5, allegation=relevant_allegation_1)
        OfficerAllegationFactory(officer=pinned_officer_2, allegation=relevant_allegation_2)

        relevant_complaints = list(pinboard.relevant_complaints)

        expect(relevant_complaints).to.have.length(2)
        expect(relevant_complaints[0].crid).to.eq('2')
        expect(relevant_complaints[0].prefetched_officer_allegations).to.have.length(1)
        expect(relevant_complaints[0].prefetched_officer_allegations[0].officer.id).to.eq(2)

        expect(relevant_complaints[1].crid).to.eq('1')
        expect(relevant_complaints[1].prefetched_officer_allegations).to.have.length(3)
        expect(relevant_complaints[1].prefetched_officer_allegations[0].officer.id).to.eq(5)
        expect(relevant_complaints[1].prefetched_officer_allegations[1].officer.id).to.eq(1)
        expect(relevant_complaints[1].prefetched_officer_allegations[2].officer.id).to.eq(4)

    def test_relevant_documents_via_accused_officers(self):
        pinned_officer_1 = OfficerFactory(id=1)
        pinned_officer_2 = OfficerFactory(id=2)
        pinned_officer_3 = OfficerFactory(id=3)
        relevant_allegation_1 = AllegationFactory(crid='1', incident_date=datetime(2002, 2, 21, tzinfo=pytz.utc))
        relevant_allegation_2 = AllegationFactory(crid='2', incident_date=datetime(2002, 2, 22, tzinfo=pytz.utc))
        not_relevant_allegation = AllegationFactory(crid='not relevant')
        relevant_document_1 = AttachmentFileFactory(
            id=1, file_type='document', owner=relevant_allegation_1, show=True
        )
        relevant_document_2 = AttachmentFileFactory(
            id=2, file_type='document', owner=relevant_allegation_2, show=True
        )
        AttachmentFileFactory(
            id=998, file_type='document', title='relevant but not show', owner=relevant_allegation_1, show=False
        )
        AttachmentFileFactory(
            id=999, file_type='document', title='not relevant', owner=not_relevant_allegation, show=True
        )

        pinboard = PinboardFactory(
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer_1, pinned_officer_2, pinned_officer_3])
        OfficerAllegationFactory(officer=pinned_officer_1, allegation=relevant_allegation_1)
        OfficerAllegationFactory(officer=pinned_officer_2, allegation=relevant_allegation_2)

        relevant_documents = list(pinboard.relevant_documents)

        expect(relevant_documents).to.have.length(2)
        expect(relevant_documents[0].id).to.eq(relevant_document_2.id)
        expect(relevant_documents[0].owner.crid).to.eq('2')
        expect(relevant_documents[1].id).to.eq(relevant_document_1.id)
        expect(relevant_documents[1].owner.crid).to.eq('1')

    def test_relevant_documents_with_pinned_allegations(self):
        pinned_officer_1 = OfficerFactory(id=1)
        pinned_officer_2 = OfficerFactory(id=2)
        pinned_allegation_1 = AllegationFactory(crid='1', incident_date=datetime(2002, 2, 21, tzinfo=pytz.utc))
        pinned_allegation_2 = AllegationFactory(crid='2', incident_date=datetime(2002, 2, 22, tzinfo=pytz.utc))
        pinboard = PinboardFactory(
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer_1, pinned_officer_2])
        pinboard.allegations.set([pinned_allegation_1, pinned_allegation_2])
        OfficerAllegationFactory(officer=pinned_officer_1, allegation=pinned_allegation_1)
        OfficerAllegationFactory(officer=pinned_officer_2, allegation=pinned_allegation_2)
        not_relevant_allegation = AllegationFactory(crid='not relevant')
        relevant_document_1 = AttachmentFileFactory(
            id=1, file_type='document', owner=pinned_allegation_1, show=True
        )
        relevant_document_2 = AttachmentFileFactory(
            id=2, file_type='document', owner=pinned_allegation_2, show=True
        )
        AttachmentFileFactory(
            id=998, file_type='document',  title='relevant but not show', owner=pinned_allegation_1, show=False
        )
        AttachmentFileFactory(
            id=999, file_type='document', title='not relevant', owner=not_relevant_allegation, show=True
        )

        relevant_documents = list(pinboard.relevant_documents)
        expect(relevant_documents).to.have.length(2)
        expect(relevant_documents[0].id).to.eq(relevant_document_2.id)
        expect(relevant_documents[0].owner.crid).to.eq('2')
        expect(relevant_documents[1].id).to.eq(relevant_document_1.id)
        expect(relevant_documents[1].owner.crid).to.eq('1')

    def test_relevant_documents_order_officers(self):
        pinned_officer_1 = OfficerFactory(id=1, allegation_count=3)
        pinned_officer_2 = OfficerFactory(id=2)
        pinned_officer_3 = OfficerFactory(id=3)
        officer_4 = OfficerFactory(id=4, allegation_count=2)
        officer_5 = OfficerFactory(id=5, allegation_count=4)
        relevant_allegation_1 = AllegationFactory(crid='1', incident_date=datetime(2002, 2, 21, tzinfo=pytz.utc))
        relevant_allegation_2 = AllegationFactory(crid='2', incident_date=datetime(2002, 2, 22, tzinfo=pytz.utc))
        not_relevant_allegation = AllegationFactory(crid='999')
        pinboard = PinboardFactory(
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer_1, pinned_officer_2, pinned_officer_3])
        OfficerAllegationFactory(officer=pinned_officer_1, allegation=relevant_allegation_1)
        OfficerAllegationFactory(officer=officer_4, allegation=relevant_allegation_1)
        OfficerAllegationFactory(officer=officer_5, allegation=relevant_allegation_1)
        OfficerAllegationFactory(officer=pinned_officer_2, allegation=relevant_allegation_2)

        relevant_document_1 = AttachmentFileFactory(
            id=1, file_type='document', owner=relevant_allegation_1, show=True
        )
        relevant_document_2 = AttachmentFileFactory(
            id=2, file_type='document', owner=relevant_allegation_2, show=True
        )
        AttachmentFileFactory(
            id=998, file_type='document', title='relevant but not show', owner=relevant_allegation_1, show=False
        )
        AttachmentFileFactory(
            id=999, file_type='document', title='not relevant', owner=not_relevant_allegation, show=True
        )

        relevant_documents = list(pinboard.relevant_documents)

        expect(relevant_documents).to.have.length(2)
        expect(relevant_documents[0].id).to.eq(relevant_document_2.id)
        expect(relevant_documents[0].owner.crid).to.eq('2')

        expect(relevant_documents[1].id).to.eq(relevant_document_1.id)
        expect(relevant_documents[1].owner.crid).to.eq('1')

    def test_relevant_documents_not_showing_audios_and_videos(self):
        pinned_officer_1 = OfficerFactory(id=1)
        relevant_allegation = AllegationFactory(crid='1', incident_date=datetime(2002, 2, 21, tzinfo=pytz.utc))
        OfficerAllegationFactory(officer=pinned_officer_1, allegation=relevant_allegation)
        AttachmentFileFactory(file_type='document', owner=relevant_allegation, show=True)
        AttachmentFileFactory(file_type='document', owner=relevant_allegation, show=True)
        AttachmentFileFactory(file_type='audio', owner=relevant_allegation, show=True)
        AttachmentFileFactory(file_type='video', owner=relevant_allegation, show=True)

        pinboard = PinboardFactory(
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer_1])

        relevant_documents = list(pinboard.relevant_documents)

        expect(relevant_documents).to.have.length(2)
        expect(relevant_documents[0].file_type).to.eq('document')
        expect(relevant_documents[1].file_type).to.eq('document')
