import pytz
import datetime
from operator import itemgetter

from django.test import TestCase
from django.contrib.gis.geos import Point

from robber import expect

from lawsuit.serializers import LawsuitSerializer
from lawsuit.factories import (
    LawsuitFactory,
    LawsuitPlaintiffFactory,
    PaymentFactory
)
from data.factories import OfficerFactory, AttachmentFileFactory
from lawsuit.cache_managers import lawsuit_cache_manager


class LawsuitSerializerTestCase(TestCase):
    def test_serializer(self):
        lawsuit = LawsuitFactory(
            case_no='00-L-5230',
            summary='Hutchinson was shot and killed outside a bar near the Addison Red Line stop.',
            primary_cause='EXCESSIVE FORCE/MINOR',
            incident_date=datetime.datetime(2000, 3, 16, 0, 0, 0, tzinfo=pytz.utc),
            location='near intersection of N Wavelandand Sheffield', add1='200', add2='E. Chicago Ave.',
            city='Chicago IL',
            point=Point(-35.5, 68.9),
            interactions=['Protest'],
            outcomes=['Killed by officer'],
            services=['On Duty', 'Plainclothes'],
            violences=['Physical Force'],
            misconducts=['Excessive force', 'Racial epithets'],
        )
        attachment = AttachmentFileFactory(owner=lawsuit, show=True, preview_image_url=None)

        LawsuitPlaintiffFactory(name='Kevin Vodak', lawsuit=lawsuit)
        LawsuitPlaintiffFactory(name='Sharon Ambielli', lawsuit=lawsuit)

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

        other_lawsuit = LawsuitFactory()
        other_lawsuit.officers.set([officer_2])

        lawsuit_cache_manager.cache_data()
        lawsuit.refresh_from_db()

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
                    'lawsuit_count': 2,
                    'total_lawsuit_settlements': '2500007500.00',
                    'rank': 'Sergeant',
                }
            ],
            'interactions': ['Protest'],
            'services': ['On Duty', 'Plainclothes'],
            'misconducts': ['Excessive force', 'Racial epithets'],
            'violences': ['Physical Force'],
            'outcomes': ['Killed by officer'],
            'point': {
                'lon': -35.5,
                'lat': 68.9,
            },
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
                'id': str(attachment.id),
                'title': attachment.title,
                'file_type': attachment.file_type,
                'url': attachment.url,
            }
        }
        serializer_data = LawsuitSerializer(lawsuit).data
        serializer_data['plaintiffs'] = sorted(serializer_data['plaintiffs'], key=itemgetter('name'))
        serializer_data['officers'] = sorted(serializer_data['officers'], key=itemgetter('full_name'))
        serializer_data['payments'] = sorted(serializer_data['payments'], key=itemgetter('payee'))

        expect(serializer_data).to.eq(expected_data)

    def test_serializer_point(self):
        lawsuit = LawsuitFactory(
            point=Point(-35.5, 68.9)
        )
        serializer_data = LawsuitSerializer(lawsuit).data
        expect(serializer_data['point']).to.eq({
            'lon': -35.5,
            'lat': 68.9,
        })

        lawsuit = LawsuitFactory(
            point=None
        )
        serializer_data = LawsuitSerializer(lawsuit).data

        expect('point' in serializer_data).to.be.false()
