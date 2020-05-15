from datetime import datetime

import pytz
from django.test import TestCase
from freezegun import freeze_time
from robber import expect

from data.factories import OfficerFactory
from pinboard.serializers.desktop.admin.officer_serializer import OfficerSerializer


class OfficerSerializerTestCase(TestCase):
    def test_serialization(self):
        with freeze_time(datetime(2018, 4, 3, 12, 0, 10, tzinfo=pytz.utc)):
            officer = OfficerFactory(
                first_name='Jerome',
                last_name='Finnigan',
                allegation_count=0,
                complaint_percentile='0.0000',
                trr_percentile='0.0000',
                civilian_allegation_percentile='0.0000',
                internal_allegation_percentile='0.0000',
            )

            expect(OfficerSerializer(officer).data).to.eq({
                'id': officer.id,
                'name': 'Jerome Finnigan',
                'count': 0,
                'percentile_allegation': '0.0000',
                'percentile_trr': '0.0000',
                'percentile_allegation_civilian': '0.0000',
                'percentile_allegation_internal': '0.0000',
            })
