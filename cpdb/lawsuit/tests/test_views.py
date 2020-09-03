import pytz
import datetime
from operator import itemgetter
import random

from robber import expect
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lawsuit.factories import (
    LawsuitFactory,
    LawsuitPlaintiffFactory,
    PaymentFactory
)
from data.factories import OfficerFactory, AttachmentFileFactory
from lawsuit.cache_managers import lawsuit_cache_manager


class LawsuitViewSetTestCase(APITestCase):
    def test_retrieve(self):
        lawsuit = LawsuitFactory(
            case_no='00-L-5230',
            summary='Hutchinson was shot and killed outside a bar near the Addison Red Line stop.',
            primary_cause='EXCESSIVE FORCE/MINOR',
            incident_date=datetime.datetime(2000, 3, 16, 0, 0, 0, tzinfo=pytz.utc),
            location='near intersection of N Wavelandand Sheffield', add1='200', add2='E. Chicago Ave.',
            city='Chicago IL',
            interactions=['Protest'],
            outcomes=['Killed by officer'],
            services=['On Duty', 'Plainclothes'],
            violences=['Physical Force'],
            misconducts=['Excessive force', 'Racial epithets'],
        )

        LawsuitPlaintiffFactory(name='Kevin Vodak', lawsuit=lawsuit)
        LawsuitPlaintiffFactory(name='Sharon Ambielli', lawsuit=lawsuit)
        attachment = AttachmentFileFactory(owner=lawsuit, preview_image_url='preview.png', url='/docs/lawsuit.pdf')
        AttachmentFileFactory(owner=lawsuit, show=False)

        officer_1 = OfficerFactory(
            first_name='Jerome',
            last_name='Finnigan',
            allegation_count=4,
            trr_percentile='11.11',
            complaint_percentile='22.22',
            civilian_allegation_percentile='33.33',
            internal_allegation_percentile='44.44',
            sustained_count=1,
            birth_year=1977,
            race='White',
            gender='M',
            rank='Police Officer',
        )
        officer_2 = OfficerFactory(
            first_name='Michael',
            last_name='Flynn',
            allegation_count=7,
            trr_percentile='55.55',
            complaint_percentile='66.66',
            civilian_allegation_percentile='77.77',
            internal_allegation_percentile='88.88',
            sustained_count=2,
            birth_year=1990,
            race='Black',
            gender='F',
            rank='Sergeant',
        )

        PaymentFactory(payee='Lucy Bells', settlement='7500', legal_fees=0, lawsuit=lawsuit)
        PaymentFactory(payee='Genre Wilson', settlement=0, legal_fees='2500000000', lawsuit=lawsuit)

        lawsuit.officers.set([officer_1, officer_2])
        lawsuit_cache_manager.cache_data()

        url = reverse('api-v2:lawsuit-detail', kwargs={'pk': '00-L-5230'})
        response = self.client.get(url)
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expected_data = {
            'case_no': '00-L-5230',
            'summary': 'Hutchinson was shot and killed outside a bar near the Addison Red Line stop.',
            'primary_cause': 'EXCESSIVE FORCE/MINOR',
            'address': '200 E. Chicago Ave., Chicago IL',
            'location': 'near intersection of N Wavelandand Sheffield',
            'incident_date': '2000-03-16',
            'plaintiffs': [
                {'name': 'Kevin Vodak'},
                {'name': 'Sharon Ambielli'}
            ],
            'officers': [
                {
                    'id': officer_1.id,
                    'full_name': 'Jerome Finnigan',
                    'allegation_count': 4,
                    'percentile_trr': '11.1100',
                    'percentile_allegation': '22.2200',
                    'percentile_allegation_civilian': '33.3300',
                    'percentile_allegation_internal': '44.4400',
                    'sustained_count': 1,
                    'birth_year': 1977,
                    'race': 'White',
                    'gender': 'Male',
                    'lawsuit_count': 1,
                    'total_lawsuit_settlements': '2500007500.00',
                    'rank': 'Police Officer',
                },
                {
                    'id': officer_2.id,
                    'full_name': 'Michael Flynn',
                    'allegation_count': 7,
                    "percentile_trr": "55.5500",
                    "percentile_allegation": "66.6600",
                    "percentile_allegation_civilian": "77.7700",
                    "percentile_allegation_internal": "88.8800",
                    'sustained_count': 2,
                    'birth_year': 1990,
                    'race': 'Black',
                    'gender': 'Female',
                    'lawsuit_count': 1,
                    'total_lawsuit_settlements': '2500007500.00',
                    'rank': 'Sergeant',
                }
            ],
            'interactions': ['Protest'],
            'services': ['On Duty', 'Plainclothes'],
            'misconducts': ['Excessive force', 'Racial epithets'],
            'violences': ['Physical Force'],
            'outcomes': ['Killed by officer'],
            'payments': [
                {
                    'payee': 'Genre Wilson',
                    'settlement': '0.00',
                    'legal_fees': '2500000000.00'
                },
                {
                    'payee': 'Lucy Bells',
                    'settlement': '7500.00',
                    'legal_fees': '0.00'
                }
            ],
            'total_payments': '2500007500.00',
            'total_settlement': '7500.00',
            'total_legal_fees': '2500000000.00',
            'attachment': {
                'id': f'{attachment.id}',
                'title': attachment.title,
                'file_type': attachment.file_type,
                'preview_image_url': 'preview.png',
                'url': '/docs/lawsuit.pdf',
            }
        }
        response_data = response.data
        response_data['plaintiffs'] = sorted(response_data['plaintiffs'], key=itemgetter('name'))
        response_data['officers'] = sorted(response_data['officers'], key=itemgetter('full_name'))
        response_data['payments'] = sorted(response_data['payments'], key=itemgetter('payee'))
        expect(response_data).to.eq(expected_data)

    def test_retrieve_not_found(self):
        url = reverse('api-v2:lawsuit-detail', kwargs={'pk': '00-L-5230'})
        response = self.client.get(url)
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)

    def test_top_lawsuits(self):
        lawsuits_ids = {LawsuitFactory(total_payments=random.uniform(1000, 10000)).id for _ in range(100)}
        for _ in range(50):
            LawsuitFactory(total_payments=random.uniform(0, 1000))

        url = reverse('api-v2:lawsuit-top-lawsuits')
        response = self.client.get(url)
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expected_lawsuits_ids = [item['id'] for item in response.data]
        expect(set(expected_lawsuits_ids).issubset(lawsuits_ids)).to.be.true()
