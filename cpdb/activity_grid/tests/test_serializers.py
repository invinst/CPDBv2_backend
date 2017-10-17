from django.test import SimpleTestCase

from robber import expect
from mock import Mock

from activity_grid.serializers import ActivityCardSerializer


class ActivityCardSerializerTestCase(SimpleTestCase):
    def test_serialize_officer_card(self):
        obj = Mock()
        obj.officer = Mock(
            full_name='ABC',
            id=10,
            visual_token_background_color='#fff'
            )

        expect(ActivityCardSerializer(obj).data).to.eq({
            'full_name': 'ABC',
            'id': 10,
            'visual_token_background_color': '#fff'
            })
