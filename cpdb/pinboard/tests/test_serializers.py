from rest_framework.test import APITestCase
from robber import expect

from data.models import Allegation
from pinboard.serializers.pinboard_complaint_serializer import PinboardComplaintSerializer


class PinboardComplaintSerializerTestCase(APITestCase):
    def test_get_point_none(self):
        allegation = Allegation(point=None)
        serializer = PinboardComplaintSerializer(allegation)
        expect(serializer.data['point']).to.eq(None)

    def test_get_most_common_category_none(self):
        allegation = Allegation(most_common_category=None)
        serializer = PinboardComplaintSerializer(allegation)
        expect(serializer.data['most_common_category']).to.eq('')
