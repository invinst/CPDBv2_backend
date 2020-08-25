from datetime import datetime

from django.test import TestCase

from robber import expect
import pytz

from search_mobile.serializers import LawsuitRSerializer
from lawsuit.factories import LawsuitFactory


class LawsuitSerializerTestCase(TestCase):
    def test_serialization(self):
        lawsuit = LawsuitFactory(
            case_no='00-L-5230',
            primary_cause='EXCESSIVE FORCE/MINOR',
            incident_date=datetime(2000, 3, 16, 0, 0, 0, tzinfo=pytz.utc),
        )

        expect(LawsuitRSerializer(lawsuit).data).to.eq({
            'id': lawsuit.id,
            'case_no': '00-L-5230',
            'primary_cause': 'EXCESSIVE FORCE/MINOR',
            'incident_date': '2000-03-16',
            'type': 'LAWSUIT',
        })
