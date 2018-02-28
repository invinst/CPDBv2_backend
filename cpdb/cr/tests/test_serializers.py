from django.test import TestCase

from robber import expect
from mock import Mock

from cr.serializers import InvolvementOfficerSerializer, CRSerializer


class InvolvementOfficerSerializerTestCase(TestCase):
    def test_get_extra_info(self):
        officer = Mock(id=1, abbr_name='M. Foo', current_badge='11111')
        result = InvolvementOfficerSerializer(officer).data
        expect(result['extra_info']).to.eq('Badge 11111')


class CRSerializerTestCase(TestCase):
    def test_get_beat_id(self):
        obj = Mock()
        obj.beat = None
        obj.involvement_set = Mock()
        obj.involvement_set.filter = Mock(return_value=[])
        obj.officer_allegations = []
        obj.complainants = []
        obj.category_names = []
        obj.documents = []
        obj.videos = []
        obj.audios = []
        result = CRSerializer(obj).data
        expect(result['beat']).to.eq(None)

        obj.beat = Mock()
        obj.beat.name = '12'
        result = CRSerializer(obj).data
        expect(result['beat']).to.eq({'name': '12'})

    def test_get_point(self):
        obj = Mock()
        obj.point = None
        obj.involvement_set = Mock()
        obj.involvement_set.filter = Mock(return_value=[])
        obj.officer_allegations = []
        obj.complainants = []
        obj.category_names = []
        obj.documents = []
        obj.videos = []
        obj.audios = []
        result = CRSerializer(obj).data
        expect(result['point']).to.eq(None)

        obj.to_dict = Mock()
        obj.point = Mock()
        obj.point.x = 1.0
        obj.point.y = 1.0
        result = CRSerializer(obj).data
        expect(result['point']).to.eq({'long': 1.0, 'lat': 1.0})

    def test_get_involvements(self):
        obj = Mock()
        obj.officer_allegations = []
        obj.complainants = []
        obj.category_names = []
        obj.documents = []
        obj.videos = []
        obj.audios = []
        obj.involvement_set = Mock()

        officer1 = Mock(id=1, abbr_name='M. Foo', gender_display='Male', race='White', current_badge='11111')
        involvement1 = Mock(officer=officer1, involved_type='commander')

        officer2 = Mock(id=2, abbr_name='M. Bar', gender_display='Female', race='Black', current_badge='22222')
        involvement2 = Mock(officer=officer2, involved_type='investigator')

        obj.involvement_set.filter = Mock(return_value=[involvement1, involvement2])
        result = CRSerializer(obj).data
        self.assertListEqual(result['involvements'], [{
            'involved_type': 'investigator',
            'officers': [{
                'id': 2,
                'abbr_name': 'M. Bar',
                'extra_info': 'Badge 22222'
            }]
        }, {
            'involved_type': 'commander',
            'officers': [{
                'id': 1,
                'abbr_name': 'M. Foo',
                'extra_info': 'Badge 11111'
            }]
        }])
