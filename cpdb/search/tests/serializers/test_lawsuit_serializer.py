import pytz
from _datetime import datetime
from operator import itemgetter

from django.test import TestCase

from robber import expect

from search.serializers import LawsuitSerializer
from lawsuit.factories import (
    LawsuitFactory,
    LawsuitPlaintiffFactory,
)
from data.factories import OfficerFactory


class LawsuitSerializerTestCase(TestCase):
    def test_serializer(self):
        lawsuit = LawsuitFactory(
            case_no='00-L-5230',
            summary='Hutchinson was shot and killed outside a bar near the Addison Red Line stop.',
            primary_cause='EXCESSIVE FORCE/MINOR',
            incident_date=datetime(2000, 3, 16, 0, 0, 0, tzinfo=pytz.utc),
            location='near intersection of N Wavelandand Sheffield', add1='200', add2='E. Chicago Ave.',
            city='Chicago IL',
            total_payments=2500007500
        )

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

        lawsuit.officers.set([officer_1, officer_2])

        lawsuit.refresh_from_db()

        expected_data = {
            'id': lawsuit.id,
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
                },
                {
                    'id': officer_2.id,
                    'full_name': 'Michael Flynn',
                    'allegation_count': 7,
                    'percentile_trr': '55.5500',
                    'percentile_allegation': '66.6600',
                    'percentile_allegation_civilian': '77.7700',
                    'percentile_allegation_internal': '88.8800',
                }
            ],
            'total_payments': '2500007500.00',
            'to': '/lawsuit/00-L-5230/',
        }
        serializer_data = LawsuitSerializer(lawsuit).data
        serializer_data['plaintiffs'] = sorted(serializer_data['plaintiffs'], key=itemgetter('name'))
        serializer_data['officers'] = sorted(serializer_data['officers'], key=itemgetter('full_name'))

        expect(serializer_data).to.eq(expected_data)
