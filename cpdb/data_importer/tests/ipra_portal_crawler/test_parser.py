from datetime import datetime

import pytz
from django.test.testcases import SimpleTestCase
from mock import MagicMock
from robber import expect

from data_importer.ipra_portal_crawler.parser import (
    TagField, MediaTypeField, AttachmentFileField, ArraySourceField,
    DateTimeField, Just, CompositeField, CharField, SimpleField,
    NotSupportedDateFormatException,
)


class SimpleFieldTest(SimpleTestCase):
    def test_parse(self):
        expect(SimpleField(field_name='key').parse('1')).to.be.eq('1')
        expect(SimpleField(field_name='key').parse(2)).to.be.eq(2)
        expect(SimpleField(field_name='key').parse({'v': 3})).to.be.eq({'v': 3})


class TagFieldTest(SimpleTestCase):
    def test_parse(self):
        expect(TagField(field_name='key').parse({'key': 'arrest report'})).to.be.eq('AR')
        expect(TagField(field_name='key').parse({'key': 'officer\'s battery report'})).to.be.eq('OBR')
        expect(TagField(field_name='key').parse({'key': 'Audio'})).to.be.eq('Audio')
        expect(TagField(field_name='key').parse({'key': 'Video'})).to.be.eq('Video')
        expect(TagField(field_name='key').parse({'key': 'who knows'})).to.be.eq('Other')


class MediaTypeFieldTest(SimpleTestCase):
    def test_parse(self):
        expect(MediaTypeField(field_name='key').parse({'key': 'Audio something'})).to.be.eq('audio')
        expect(MediaTypeField(field_name='key').parse({'key': 'Video something'})).to.be.eq('video')
        expect(MediaTypeField(field_name='key').parse({'key': 'something else'})).to.be.eq('document')


class AttachmentFileFieldTest(SimpleTestCase):
    def test_parse(self):
        expect(AttachmentFileField().parse({
            'type': 'Audio something',
            'title': 'title',
            'link': '//this_is_a_link',
            'last_updated': '2018-10-30T15:00:03+00:00',
        })).to.be.eq({
            'file_type': 'audio',
            'title': 'title',
            'url': '//this_is_a_link',
            'original_url': '//this_is_a_link',
            'tag': 'Other',
            'source_type': 'COPA',
            'last_updated': datetime(2018, 10, 30, 15, 0, 3, tzinfo=pytz.utc),
        })


class ArraySourceFieldTest(SimpleTestCase):
    class SampleParser(object):
        def parse(self, value):
            return value

    def test_parse(self):
        expect(ArraySourceField(field_name='key', parser=self.SampleParser()).parse({
            'key': [1, 2, 3]
        })).to.be.eq([1, 2, 3])


class DateTimeFieldTest(SimpleTestCase):
    def test_parse(self):
        expect(DateTimeField(field_name='key').parse({'key': '1-4-2011 9:35 PM'})).to.be.eq(
            datetime(month=1, day=4, year=2011, hour=21, minute=35))

        expect(
            DateTimeField(field_name='key').parse({'key': '2018-10-30T15:00:03+00:00'})
        ).to.be.eq(datetime(2018, 10, 30, 15, 0, 3, tzinfo=pytz.utc))

        expect(DateTimeField(field_name='key').parse({'other_key': '1-4-2011 9:35 PM'})).to.be.none()

        expect(
            lambda: DateTimeField(field_name='key').parse({'key': '2011-23-23 9:35 PM'})
        ).to.throw(NotSupportedDateFormatException)


class CompositeFieldTest(SimpleTestCase):
    def test_parse(self):
        custom_field = MagicMock()
        custom_field.parse.return_value = 'parsed'

        expect(CompositeField(layout={'key': custom_field}).parse({'key': ''})).to.eq({'key': 'parsed'})
        expect(custom_field.parse).to.be.called()

    def test_parse_empty_field(self):
        empty_field = MagicMock()
        empty_field.parse.return_value = None
        expect(CompositeField(layout={'key': empty_field}).parse({'key': ''})).to.be.none()
        expect(CompositeField().parse({'key': ''})).to.be.none()


class JustTest(SimpleTestCase):
    def test_parse(self):
        expect(Just('something').parse('anything')).to.be.eq('something')


class CharFieldTest(SimpleTestCase):
    def test_parse(self):
        expect(CharField().parse({'key': 'value'})).to.be.eq('')
        expect(CharField(field_name='key').parse({'key': 'value'})).to.be.eq('value')

    def test_parser_none_should_return_empty_string(self):
        expect(CharField(field_name='key').parse({'key': None})).to.be.eq('')
