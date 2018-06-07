from datetime import datetime, date

from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Point

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect

from data.factories import PoliceUnitFactory, OfficerFactory, OfficerHistoryFactory, OfficerAllegationFactory
from trr.factories import TRRFactory, ActionResponseFactory
from trr.tests.mixins import TRRTestCaseMixin


class TRRViewSetTestCase(TRRTestCaseMixin, APITestCase):
    def test_retrieve(self):
        unit = PoliceUnitFactory(unit_name='001', description='Unit 001')
        officer = OfficerFactory(
            first_name='Vinh',
            last_name='Vu',
            race='White',
            gender='M',
            appointed_date=date(2000, 1, 1),
            birth_year=1980)
        OfficerHistoryFactory(officer=officer, unit=unit)
        trr = TRRFactory(
            taser=False,
            firearm_used=False,
            officer_assigned_beat='Beat 1',
            officer_in_uniform=True,
            officer_on_duty=False,
            trr_datetime=datetime(2001, 1, 1),
            subject_gender='M',
            subject_age=37,
            officer=officer,
            location_recode='Factory',
            block='34XX',
            street='Douglas Blvd',
            beat=1021,
            point=Point(1.0, 1.0),
        )
        OfficerAllegationFactory(
            officer=officer,
            allegation__incident_date=datetime(2003, 1, 1),
            start_date=date(2004, 1, 1),
            end_date=date(2005, 1, 1),
            final_finding='SU'
        )
        ActionResponseFactory(trr=trr, force_type='Verbal Commands', action_sub_category='1')

        self.refresh_index()

        response = self.client.get(reverse('api-v2:trr-detail', kwargs={'pk': trr.id}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)

        expect(response.data).to.eq({
            'id': trr.id,
            'officer_assigned_beat': 'Beat 1',
            'officer_in_uniform': True,
            'officer_on_duty': False,
            'officer': {
                'id': officer.id,
                'gender': 'Male',
                'race': 'White',
                'full_name': 'Vinh Vu',
                'appointed_date': '2000-01-01',
                'unit': {'unit_name': '001', 'description': 'Unit 001'},
                'birth_year': 1980,
                'percentile_trr': 0.0,
                'percentile_allegation_internal': 0.0,
                'percentile_allegation_civilian': 0.0,
            },
            'subject_race': 'White',
            'subject_gender': 'Male',
            'subject_age': 37,
            'force_category': 'Other',
            'force_types': ['Verbal Commands'],
            'date_of_incident': '2001-01-01',
            'location_type': 'Factory',
            'address': '34XX Douglas Blvd',
            'beat': 1021,
            'point': {
                'lng': 1.0,
                'lat': 1.0,
            },
        })

    def test_retrieve_no_point(self):
        unit = PoliceUnitFactory(unit_name='001', description='Unit 001')
        officer = OfficerFactory(
            first_name='Vinh',
            last_name='Vu',
            race='White',
            gender='M',
            appointed_date=date(2000, 1, 1),
            birth_year=1980)
        OfficerHistoryFactory(officer=officer, unit=unit)
        trr = TRRFactory(
            taser=False,
            firearm_used=False,
            officer_assigned_beat='Beat 1',
            officer_in_uniform=True,
            officer_on_duty=False,
            trr_datetime=datetime(2001, 1, 1),
            subject_gender='M',
            subject_age=37,
            officer=officer,
            location_recode='Factory',
            block='34XX',
            street='Douglas Blvd',
            beat=1021,
        )
        OfficerAllegationFactory(
            officer=officer,
            allegation__incident_date=datetime(2003, 1, 1),
            start_date=date(2004, 1, 1),
            end_date=date(2005, 1, 1), final_finding='SU')
        ActionResponseFactory(trr=trr, force_type='Verbal Commands', action_sub_category=1)

        self.refresh_index()

        response = self.client.get(reverse('api-v2:trr-detail', kwargs={'pk': trr.id}))
        expect(response.status_code).to.eq(status.HTTP_200_OK)

        expect(response.data).to.eq({
            'id': trr.id,
            'officer_assigned_beat': 'Beat 1',
            'officer_in_uniform': True,
            'officer_on_duty': False,
            'officer': {
                'id': officer.id,
                'gender': 'Male',
                'race': 'White',
                'full_name': 'Vinh Vu',
                'appointed_date': '2000-01-01',
                'unit': {'unit_name': '001', 'description': 'Unit 001'},
                'birth_year': 1980,
                'percentile_trr': 0.0,
                'percentile_allegation_internal': 0.0,
                'percentile_allegation_civilian': 0.0,
            },
            'subject_race': 'White',
            'subject_gender': 'Male',
            'subject_age': 37,
            'force_category': 'Other',
            'force_types': ['Verbal Commands'],
            'date_of_incident': '2001-01-01',
            'location_type': 'Factory',
            'address': '34XX Douglas Blvd',
            'beat': 1021,
            'point': {
                'lng': None,
                'lat': None,
            },
        })

    def test_retrieve_not_found(self):
        response = self.client.get(reverse('api-v2:trr-detail', kwargs={'pk': 123}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_request_document(self):
        TRRFactory(pk=112233)
        response = self.client.post(
            reverse('api-v2:trr-request-document', kwargs={'pk': 112233}),
            {'email': 'valid_email@example.com'}
        )
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'message': 'Thanks for subscribing',
            'trr_id': 112233
        })

    def test_request_same_document_twice(self):
        trr = TRRFactory(pk=112233)
        self.client.post(
            reverse('api-v2:trr-request-document', kwargs={'pk': trr.id}),
            {'email': 'valid_email@example.com'}
        )

        response2 = self.client.post(
            reverse('api-v2:trr-request-document', kwargs={'pk': trr.id}),
            {'email': 'valid_email@example.com'}
        )
        expect(response2.status_code).to.eq(status.HTTP_200_OK)
        expect(response2.data).to.eq({
            'message': 'Email already added',
            'trr_id': 112233
        })

    def test_request_document_without_email(self):
        TRRFactory(pk=321)
        response = self.client.post(reverse('api-v2:trr-request-document', kwargs={'pk': 321}))
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(response.data).to.eq({
            'message': 'Please enter a valid email'
        })

    def test_request_document_with_invalid_email(self):
        TRRFactory(pk=321)
        response = self.client.post(reverse('api-v2:trr-request-document', kwargs={'pk': 321}),
                                    {'email': 'invalid@email'})
        expect(response.status_code).to.eq(status.HTTP_400_BAD_REQUEST)
        expect(response.data).to.eq({
            'message': 'Please enter a valid email'
        })

    def test_request_document_with_invalid_trr(self):
        response = self.client.post(reverse('api-v2:trr-request-document', kwargs={'pk': 321}))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)
