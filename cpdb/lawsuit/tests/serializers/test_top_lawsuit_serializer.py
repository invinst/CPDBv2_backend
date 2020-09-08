import pytz
import datetime

from django.test import TestCase

from robber import expect

from lawsuit.serializers import TopLawsuitSerializer
from lawsuit.factories import LawsuitFactory


class LawsuitSerializerTestCase(TestCase):
    def test_serializer(self):
        lawsuit = LawsuitFactory(
            case_no='00-L-5230',
            summary='Hutchinson was shot and killed outside a bar near the Addison Red Line stop.',
            primary_cause='EXCESSIVE FORCE/MINOR',
            incident_date=datetime.datetime(2000, 3, 16, 0, 0, 0, tzinfo=pytz.utc),
        )

        expected_data = {
            'id': lawsuit.id,
            'case_no': '00-L-5230',
            'summary': 'Hutchinson was shot and killed outside a bar near the Addison Red Line stop.',
            'primary_cause': 'EXCESSIVE FORCE/MINOR',
            'incident_date': '2000-03-16',
        }

        serializer_data = TopLawsuitSerializer(lawsuit).data

        expect(serializer_data).to.eq(expected_data)
