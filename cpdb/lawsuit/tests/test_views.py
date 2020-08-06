import pytz
import datetime
from operator import itemgetter

from robber import expect
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lawsuit.factories import (
    LawsuitFactory,
    LawsuitPlaintiffFactory,
    LawsuitInteractionFactory,
    LawsuitServiceFactory,
    LawsuitMisconductFactory,
    LawsuitViolenceFactory,
    LawsuitOutcomeFactory,
    PaymentFactory
)
from data.factories import OfficerFactory, AttachmentFileFactory


class LawsuitViewSetTestCase(APITestCase):
    def test_retrieve(self):
        lawsuit = LawsuitFactory(
            case_no='00-L-5230',
            summary='Hutchinson was shot and killed outside a bar near the Addison Red Line stop.',
            incident_date=datetime.datetime(2000, 3, 16, 0, 0, 0, tzinfo=pytz.utc),
            location='near intersection of N Wavelandand Sheffield', add1='200', add2='E. Chicago Ave.',
            city='Chicago IL'
        )

        LawsuitPlaintiffFactory(name='Kevin Vodak', lawsuit=lawsuit)
        LawsuitPlaintiffFactory(name='Sharon Ambielli', lawsuit=lawsuit)

        interaction = LawsuitInteractionFactory(name='Protest')
        outcome = LawsuitOutcomeFactory(name='Killed by officer')
        service_1 = LawsuitServiceFactory(name='On Duty')
        service_2 = LawsuitServiceFactory(name='Plainclothes')
        violence = LawsuitViolenceFactory(name='Physical Force')
        misconduct_1 = LawsuitMisconductFactory(name='Excessive force')
        misconduct_2 = LawsuitMisconductFactory(name='Racial epithets')
        attachment = AttachmentFileFactory(owner=lawsuit, preview_image_url='preview.png', url='/docs/lawsuit.pdf')
        AttachmentFileFactory(show=False)
        AttachmentFileFactory(show=True, tag='OCIR')

        officer_1 = OfficerFactory(
            first_name='Jerome',
            last_name='Finnigan',
            allegation_count=4,
            trr_percentile='11.11',
            complaint_percentile='22.22',
            civilian_allegation_percentile='33.33',
            internal_allegation_percentile='44.44',
        )
        officer_2 = OfficerFactory(
            first_name='Michael',
            last_name='Flynn',
            allegation_count=7,
            trr_percentile='55.55',
            complaint_percentile='66.66',
            civilian_allegation_percentile='77.77',
            internal_allegation_percentile='88.88',
        )

        PaymentFactory(payee='Lucy Bells', settlement='7500', legal_fees=None, lawsuit=lawsuit)
        PaymentFactory(payee='Genre Wilson', settlement=None, legal_fees='2500000000', lawsuit=lawsuit)

        lawsuit.interactions.set([interaction])
        lawsuit.outcomes.set([outcome])
        lawsuit.services.set([service_1, service_2])
        lawsuit.violences.set([violence])
        lawsuit.misconducts.set([misconduct_1, misconduct_2])
        lawsuit.officers.set([officer_1, officer_2])

        url = reverse('api-v2:lawsuit-detail', kwargs={'pk': '00-L-5230'})
        response = self.client.get(url)
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expected_data = {
            'case_no': '00-L-5230',
            'summary': 'Hutchinson was shot and killed outside a bar near the Addison Red Line stop.',
            'address': '200 E. Chicago Ave., Chicago IL',
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
                    'sustained_count': officer_1.sustained_count,
                    'birth_year': officer_1.birth_year,
                    'race': officer_1.race,
                    'gender': officer_1.gender,
                    'lawsuit_count': 1,
                    'lawsuit_payment': '2500007500.00',
                },
                {
                    'id': officer_2.id,
                    'full_name': 'Michael Flynn',
                    'allegation_count': 7,
                    "percentile_trr": "55.5500",
                    "percentile_allegation": "66.6600",
                    "percentile_allegation_civilian": "77.7700",
                    "percentile_allegation_internal": "88.8800",
                    'sustained_count': officer_2.sustained_count,
                    'birth_year': officer_2.birth_year,
                    'race': officer_2.race,
                    'gender': officer_2.gender,
                    'lawsuit_count': 1,
                    'lawsuit_payment': '2500007500.00',
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
                    'legal_fees': '2500000000.00'
                },
                {
                    'payee': 'Lucy Bells',
                    'settlement': '7500.00'
                }
            ],
            'total_payments': {
                'total': '2500007500.00',
                'total_settlement': '7500.00',
                'total_legal_fees': '2500000000.00'
            },
            'attachments': [{
                'id': f'{attachment.id}',
                'title': attachment.title,
                'file_type': attachment.file_type,
                'preview_image_url': 'preview.png',
                'url': '/docs/lawsuit.pdf',
            }]
        }
        response_data = response.data
        response_data['plaintiffs'] = sorted(response_data['plaintiffs'], key=itemgetter('name'))
        response_data['services'] = sorted(response_data['services'])
        response_data['misconducts'] = sorted(response_data['misconducts'])
        response_data['officers'] = sorted(response_data['officers'], key=itemgetter('full_name'))
        response_data['payments'] = sorted(response_data['payments'], key=itemgetter('payee'))
        expect(response_data).to.eq(expected_data)

    def test_retrieve_not_found(self):
        url = reverse('api-v2:lawsuit-detail', kwargs={'pk': '00-L-5230'})
        response = self.client.get(url)
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)
