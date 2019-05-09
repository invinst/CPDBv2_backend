from datetime import datetime

from django.test.testcases import TestCase

import pytz
from robber.expect import expect

from data.factories import (
    AllegationFactory, OfficerFactory, OfficerAllegationFactory, InvestigatorAllegationFactory,
    PoliceWitnessFactory,
    AttachmentFileFactory,
)
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
        expect(relevant_complaints[0].prefetch_officer_allegations).to.have.length(1)
        expect(relevant_complaints[0].prefetch_officer_allegations[0].officer.id).to.eq(2)

        expect(relevant_complaints[1].crid).to.eq('1')
        expect(relevant_complaints[1].prefetch_officer_allegations).to.have.length(3)
        expect(relevant_complaints[1].prefetch_officer_allegations[0].officer.id).to.eq(5)
        expect(relevant_complaints[1].prefetch_officer_allegations[1].officer.id).to.eq(1)
        expect(relevant_complaints[1].prefetch_officer_allegations[2].officer.id).to.eq(4)

    def test_relevant_documents_via_accused_officers(self):
        pinned_officer_1 = OfficerFactory(id=1)
        pinned_officer_2 = OfficerFactory(id=2)
        pinned_officer_3 = OfficerFactory(id=3)
        relevant_allegation_1 = AllegationFactory(crid='1', incident_date=datetime(2002, 2, 21, tzinfo=pytz.utc))
        relevant_allegation_2 = AllegationFactory(crid='2', incident_date=datetime(2002, 2, 22, tzinfo=pytz.utc))
        not_relevant_allegation = AllegationFactory(crid='not relevant')
        relevant_document_1 = AttachmentFileFactory(id=1, allegation=relevant_allegation_1, show=True)
        relevant_document_2 = AttachmentFileFactory(id=2, allegation=relevant_allegation_2, show=True)
        AttachmentFileFactory(id=998, title='relevant but not show', allegation=relevant_allegation_1, show=False)
        AttachmentFileFactory(id=999, title='not relevant', allegation=not_relevant_allegation, show=True)

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
        expect(relevant_documents[0].allegation.crid).to.eq('2')
        expect(relevant_documents[1].id).to.eq(relevant_document_1.id)
        expect(relevant_documents[1].allegation.crid).to.eq('1')

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
        relevant_document_1 = AttachmentFileFactory(id=1, allegation=pinned_allegation_1, show=True)
        relevant_document_2 = AttachmentFileFactory(id=2, allegation=pinned_allegation_2, show=True)
        AttachmentFileFactory(id=998, title='relevant but not show', allegation=pinned_allegation_1, show=False)
        AttachmentFileFactory(id=999, title='not relevant', allegation=not_relevant_allegation, show=True)

        relevant_documents = list(pinboard.relevant_documents)
        expect(relevant_documents).to.have.length(2)
        expect(relevant_documents[0].id).to.eq(relevant_document_2.id)
        expect(relevant_documents[0].allegation.crid).to.eq('2')
        expect(relevant_documents[1].id).to.eq(relevant_document_1.id)
        expect(relevant_documents[1].allegation.crid).to.eq('1')

    def test_relevant_documents_via_investigator(self):
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

        relevant_document_1 = AttachmentFileFactory(id=1, allegation=relevant_allegation_1, show=True)
        relevant_document_2 = AttachmentFileFactory(id=2, allegation=relevant_allegation_2, show=True)
        relevant_document_3 = AttachmentFileFactory(id=3, allegation=relevant_allegation_3, show=True)
        AttachmentFileFactory(id=998, title='relevant but not show', allegation=relevant_allegation_1, show=False)
        AttachmentFileFactory(id=999, title='not relevant', allegation=not_relevant_allegation, show=True)

        relevant_documents = list(pinboard.relevant_documents)

        expect(relevant_documents).to.have.length(3)
        expect(relevant_documents[0].id).to.eq(relevant_document_3.id)
        expect(relevant_documents[0].allegation.crid).to.eq('3')
        expect(relevant_documents[1].id).to.eq(relevant_document_2.id)
        expect(relevant_documents[1].allegation.crid).to.eq('2')
        expect(relevant_documents[2].id).to.eq(relevant_document_1.id)
        expect(relevant_documents[2].allegation.crid).to.eq('1')

    def test_relevant_documents_via_police_witnesses(self):
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

        relevant_document_1 = AttachmentFileFactory(id=1, allegation=relevant_allegation_11, show=True)
        relevant_document_2 = AttachmentFileFactory(id=2, allegation=relevant_allegation_12, show=True)
        relevant_document_3 = AttachmentFileFactory(id=3, allegation=relevant_allegation_21, show=True)
        AttachmentFileFactory(id=998, title='relevant but not show', allegation=relevant_allegation_11, show=False)
        AttachmentFileFactory(id=999, title='not relevant', allegation=not_relevant_allegation, show=True)

        relevant_documents = list(pinboard.relevant_documents)

        expect(relevant_documents).to.have.length(3)
        expect(relevant_documents[0].id).to.eq(relevant_document_3.id)
        expect(relevant_documents[0].allegation.crid).to.eq('21')
        expect(relevant_documents[1].id).to.eq(relevant_document_2.id)
        expect(relevant_documents[1].allegation.crid).to.eq('12')
        expect(relevant_documents[2].id).to.eq(relevant_document_1.id)
        expect(relevant_documents[2].allegation.crid).to.eq('11')

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

        relevant_document_1 = AttachmentFileFactory(id=1, allegation=relevant_allegation_1, show=True)
        relevant_document_2 = AttachmentFileFactory(id=2, allegation=relevant_allegation_2, show=True)
        AttachmentFileFactory(id=998, title='relevant but not show', allegation=relevant_allegation_1, show=False)
        AttachmentFileFactory(id=999, title='not relevant', allegation=not_relevant_allegation, show=True)

        relevant_documents = list(pinboard.relevant_documents)

        expect(relevant_documents).to.have.length(2)
        expect(relevant_documents[0].id).to.eq(relevant_document_2.id)
        expect(relevant_documents[0].allegation.crid).to.eq('2')
        expect(relevant_documents[0].allegation.prefetch_officer_allegations).to.have.length(1)
        expect(relevant_documents[0].allegation.prefetch_officer_allegations[0].officer.id).to.eq(2)

        expect(relevant_documents[1].id).to.eq(relevant_document_1.id)
        expect(relevant_documents[1].allegation.crid).to.eq('1')
        expect(relevant_documents[1].allegation.prefetch_officer_allegations).to.have.length(3)
        expect(relevant_documents[1].allegation.prefetch_officer_allegations[0].officer.id).to.eq(5)
        expect(relevant_documents[1].allegation.prefetch_officer_allegations[1].officer.id).to.eq(1)
        expect(relevant_documents[1].allegation.prefetch_officer_allegations[2].officer.id).to.eq(4)
