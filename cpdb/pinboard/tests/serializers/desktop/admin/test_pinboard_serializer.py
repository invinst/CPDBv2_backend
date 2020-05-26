from datetime import datetime

import pytz
from django.test import TestCase
from freezegun import freeze_time
from robber import expect

from data.factories import OfficerFactory, AllegationFactory, AllegationCategoryFactory
from pinboard.factories import PinboardFactory
from pinboard.serializers.desktop.admin.pinboard_serializer import PinboardSerializer
from trr.factories import TRRFactory, ActionResponseFactory


class PinboardSerializerTestCase(TestCase):
    def test_serialization(self):
        with freeze_time(datetime(2018, 4, 3, 12, 0, 10, tzinfo=pytz.utc)):
            officer_1 = OfficerFactory(
                first_name='Jerome',
                last_name='Finnigan',
                allegation_count=0,
                complaint_percentile='0.0000',
                trr_percentile='0.0000',
                civilian_allegation_percentile='0.0000',
                internal_allegation_percentile='0.0000',
            )
            officer_2 = OfficerFactory(
                first_name='Joe',
                last_name='Parker',
                allegation_count=5,
                complaint_percentile='50.0000',
                trr_percentile='50.0000',
                civilian_allegation_percentile='50.0000',
                internal_allegation_percentile='50.0000',
            )
            officer_3 = OfficerFactory(
                first_name='John',
                last_name='Hurley',
                allegation_count=10,
                complaint_percentile='99.9999',
                trr_percentile='99.9999',
                civilian_allegation_percentile='99.9999',
                internal_allegation_percentile='99.9999',
            )
            allegation_1 = AllegationFactory(
                crid='111111',
                most_common_category=AllegationCategoryFactory(category='Use Of Force'),
                incident_date=datetime(2001, 1, 1, tzinfo=pytz.utc),
            )
            allegation_2 = AllegationFactory(
                crid='222222',
                incident_date=datetime(2002, 2, 2, tzinfo=pytz.utc),
            )
            trr_1 = TRRFactory(
                id='111',
                trr_datetime=datetime(2001, 1, 1, tzinfo=pytz.utc)
            )
            ActionResponseFactory(trr=trr_1, force_type='Use Of Force')
            trr_2 = TRRFactory(
                id='222',
                trr_datetime=datetime(2002, 2, 2, tzinfo=pytz.utc)
            )
            pinboard = PinboardFactory(
                id='aaaa1111',
                title='Pinboard 1',
                description='Pinboard description 1',
                officers=[officer_1, officer_2, officer_3],
                allegations=[allegation_1, allegation_2],
                trrs=[trr_1, trr_2],
            )
            setattr(pinboard, 'child_pinboard_count', 2)

            expect(PinboardSerializer(pinboard).data).to.eq({
                'id': 'aaaa1111',
                'title': 'Pinboard 1',
                'description': 'Pinboard description 1',
                'created_at': '2018-04-03T12:00:10Z',
                'officers_count': 3,
                'allegations_count': 2,
                'trrs_count': 2,
                'child_pinboard_count': 2,
                'officers': [
                    {
                        'id': officer_3.id,
                        'name': 'John Hurley',
                        'count': 10,
                        'percentile_allegation': '99.9999',
                        'percentile_trr': '99.9999',
                        'percentile_allegation_civilian': '99.9999',
                        'percentile_allegation_internal': '99.9999',
                    },
                    {
                        'id': officer_2.id,
                        'name': 'Joe Parker',
                        'count': 5,
                        'percentile_allegation': '50.0000',
                        'percentile_trr': '50.0000',
                        'percentile_allegation_civilian': '50.0000',
                        'percentile_allegation_internal': '50.0000',
                    },
                    {
                        'id': officer_1.id,
                        'name': 'Jerome Finnigan',
                        'count': 0,
                        'percentile_allegation': '0.0000',
                        'percentile_trr': '0.0000',
                        'percentile_allegation_civilian': '0.0000',
                        'percentile_allegation_internal': '0.0000',
                    },
                ],
                'allegations': [
                    {
                        'crid': '222222',
                        'category': 'Unknown',
                        'incident_date': '2002-02-02',
                    },
                    {
                        'crid': '111111',
                        'category': 'Use Of Force',
                        'incident_date': '2001-01-01',
                    },
                ],
                'trrs': [
                    {
                        'id': 222,
                        'trr_datetime': '2002-02-02',
                        'category': 'Unknown',
                    },
                    {
                        'id': 111,
                        'trr_datetime': '2001-01-01',
                        'category': 'Use Of Force',
                    }
                ],
            })
