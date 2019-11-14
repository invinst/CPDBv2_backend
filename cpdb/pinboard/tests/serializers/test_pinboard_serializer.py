from datetime import datetime

from django.test import TestCase

from robber import expect
from freezegun import freeze_time
import pytz

from pinboard.serializers.pinboard_serializer import (
    PinboardSerializer,
    PinboardDetailSerializer,
)
from pinboard.serializers.pinboard_admin_serializer import PinboardItemSerializer
from data.factories import OfficerFactory, AllegationFactory, AllegationCategoryFactory
from pinboard.factories import PinboardFactory
from trr.factories import TRRFactory, ActionResponseFactory


class PinboardDetailSerializerTestCase(TestCase):
    def test_serialization_without_data(self):
        pinned_officer = OfficerFactory(id=1)
        pinned_allegation = AllegationFactory(crid='1')
        pinboard = PinboardFactory(
            id='66ef1560',
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer])
        pinboard.allegations.set([pinned_allegation])

        expect(PinboardDetailSerializer(pinboard).data).to.eq({
            'id': '66ef1560',
            'title': 'Test pinboard',
            'description': 'Test description',
            'officer_ids': [1],
            'crids': ['1'],
            'trr_ids': [],
        })

    def test_serialization_with_data(self):
        pinned_officer = OfficerFactory(id=1)
        pinned_allegation = AllegationFactory(crid='1')
        pinboard = PinboardFactory(
            id='66ef1560',
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer])
        pinboard.allegations.set([pinned_allegation])

        pinboard_data = {
            'id': '123abc',
            'title': 'title',
            'description': 'description',
            'officer_ids': [1],
            'crids': ['1'],
            'trr_ids': [],
        }

        serializer = PinboardDetailSerializer(data=pinboard_data)
        expect(serializer.is_valid()).to.be.true()
        expect(serializer.data).to.eq({
            'title': 'title',
            'description': 'description',
            'officer_ids': [1],
            'crids': ['1'],
            'trr_ids': [],
        })

    def test_serialization_with_non_existing_pinned_item_ids(self):
        pinned_officer = OfficerFactory(id=1)
        pinned_allegation = AllegationFactory(crid='123abc')
        pinboard = PinboardFactory(
            id='66ef1560',
            title='Test pinboard',
            description='Test description',
        )
        pinboard.officers.set([pinned_officer])
        pinboard.allegations.set([pinned_allegation])

        pinboard_data = {
            'id': '123abc',
            'title': 'title',
            'description': 'description',
            'officer_ids': [1, 2, 4, 5],
            'crids': ['xyz789', '123abc', '456def'],
            'trr_ids': [0, 3, 1],
        }

        serializer = PinboardDetailSerializer(data=pinboard_data)
        expect(serializer.is_valid()).to.be.true()
        expect(serializer.data).to.eq({
            'title': 'title',
            'description': 'description',
            'officer_ids': [1],
            'crids': ['123abc'],
            'trr_ids': [],
            'not_found_items': {
                'officer_ids': [2, 4, 5],
                'crids':  ['xyz789', '456def'],
                'trr_ids': [0, 3, 1],
            }
        })


class PinboardSerializerTestCase(TestCase):
    def test_serialization(self):
        with freeze_time(datetime(2018, 4, 3, 12, 0, 10, tzinfo=pytz.utc)):
            pinboard = PinboardFactory(id='eeee1111', title='Pinboard 1',)

        expect(PinboardSerializer(pinboard).data).to.eq({
            'id': 'eeee1111',
            'title': 'Pinboard 1',
            'created_at': '2018-04-03',
        })


class PinboardItemSerializerTestCase(TestCase):
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

            expect(PinboardItemSerializer(pinboard).data).to.eq({
                'id': 'aaaa1111',
                'title': 'Pinboard 1',
                'description': 'Pinboard description 1',
                'created_at': '2018-04-03T12:00:10Z',
                'officers_count': 3,
                'allegations_count': 2,
                'trrs_count': 2,
                'officers': [
                    {
                        'id': officer_3.id,
                        'name': 'John Hurley',
                        'count': 10,
                        'percentile_allegation': '99.9999',
                        'percentile_trr': '99.9999',
                        'percentile_allegation_civilian': '99.9999',
                        'percentile_allegation_internal': '99.9999',
                        'year': 2016,
                    },
                    {
                        'id': officer_2.id,
                        'name': 'Joe Parker',
                        'count': 5,
                        'percentile_allegation': '50.0000',
                        'percentile_trr': '50.0000',
                        'percentile_allegation_civilian': '50.0000',
                        'percentile_allegation_internal': '50.0000',
                        'year': 2016,
                    },
                    {
                        'id': officer_1.id,
                        'name': 'Jerome Finnigan',
                        'count': 0,
                        'percentile_allegation': '0.0000',
                        'percentile_trr': '0.0000',
                        'percentile_allegation_civilian': '0.0000',
                        'percentile_allegation_internal': '0.0000',
                        'year': 2016,
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
