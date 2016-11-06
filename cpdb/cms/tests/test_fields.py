from django.test import SimpleTestCase

from mock import patch
from freezegun import freeze_time

from cms.fields import (
    LinkField, DateField, PlainTextField, MultilineTextField, RandomizerField,
    StringField, RichTextField)
from cms.randomizers import RANDOMIZER_STRATEGIES


class StringFieldTestCase(SimpleTestCase):
    def setUp(self):
        self.string_field = StringField(fake_value='CPDB')
        self.string_field.field_name = 'vftg_title'

    def test_to_representation(self):
        self.assertDictEqual(
            self.string_field.to_representation({
                'vftg_title_value': 'abc'
                }),
            {
                'name': 'vftg_title',
                'type': 'string',
                'value': 'abc'
            })

    def test_fake_data(self):
        self.assertDictEqual(
            self.string_field.fake_data(),
            {
                'name': 'vftg_title',
                'type': 'string',
                'value': 'CPDB'
            })

    def test_to_internal_value(self):
        self.assertDictEqual(
            self.string_field.to_internal_value('abc'),
            {
                'vftg_title_type': 'string',
                'vftg_title_value': 'abc'
            })


class LinkFieldTestCase(SimpleTestCase):
    def setUp(self):
        self.link_field = LinkField(fake_value='http://google.com')
        self.link_field.field_name = 'vftg_link'

    def test_to_representation(self):
        self.assertDictEqual(
            self.link_field.to_representation({
                'vftg_link_value': 'http://abc.xyz'
                }),
            {
                'name': 'vftg_link',
                'type': 'link',
                'value': 'http://abc.xyz'
            })

    def test_fake_data(self):
        self.assertDictEqual(
            self.link_field.fake_data(),
            {
                'name': 'vftg_link',
                'type': 'link',
                'value': 'http://google.com'
            })

    def test_to_internal_value(self):
        self.assertDictEqual(
            self.link_field.to_internal_value('http://abc.com'),
            {
                'vftg_link_type': 'link',
                'vftg_link_value': 'http://abc.com'
            })


class DateFieldTestCase(SimpleTestCase):
    def setUp(self):
        self.date_field = DateField()
        self.date_field.field_name = 'vftg_date'

    def test_to_representation(self):
        self.assertDictEqual(
            self.date_field.to_representation({
                'vftg_date_value': '2016-01-01'
                }),
            {
                'name': 'vftg_date',
                'type': 'date',
                'value': '2016-01-01'
            })

    @freeze_time('2012-01-14')
    def test_fake_data(self):
        self.assertDictEqual(
            self.date_field.fake_data(),
            {
                'name': 'vftg_date',
                'type': 'date',
                'value': '2012-01-14'
            })

    def test_to_internal_value(self):
        self.assertDictEqual(
            self.date_field.to_internal_value('2016-06-06'),
            {
                'vftg_date_type': 'date',
                'vftg_date_value': '2016-06-06'
            })


class PlainTextFieldTestCase(SimpleTestCase):
    def setUp(self):
        self.plain_text_field = PlainTextField(fake_value='About')
        self.plain_text_field.field_name = 'about_header'

    def test_to_representation(self):
        self.assertDictEqual(
            self.plain_text_field.to_representation({
                'about_header_value': {
                    'a': 'b'
                }
            }),
            {
                'name': 'about_header',
                'type': 'plain_text',
                'value': {
                    'a': 'b'
                }
            })

    def test_fake_data(self):
        with patch('cms.fields.generate_draft_block_key', return_value='1'):
            self.assertDictEqual(
                self.plain_text_field.fake_data(),
                {
                    'name': 'about_header',
                    'type': 'plain_text',
                    'value': {
                        'blocks': [{
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': '1',
                            'text': 'About',
                            'type': 'unstyled'
                        }],
                        'entityMap': {}
                    }
                })

    def test_to_internal_value(self):
        self.assertDictEqual(
            self.plain_text_field.to_internal_value({'c': 'd'}),
            {
                'about_header_type': 'plain_text',
                'about_header_value': {
                    'c': 'd'
                }
            })


class MultilineTextFieldTestCase(SimpleTestCase):
    _type = 'multiline_text'

    def setUp(self):
        self.field = MultilineTextField(fake_value=['abc', 'xyz'])
        self.field.field_name = 'about_content'

    def test_to_representation(self):
        self.assertDictEqual(
            self.field.to_representation({
                'about_content_value': {
                    'a': 'b'
                }
            }),
            {
                'name': 'about_content',
                'type': self._type,
                'value': {
                    'a': 'b'
                }
            })

    def test_fake_data(self):
        with patch('cms.fields.generate_draft_block_key', return_value='1'):
            self.assertDictEqual(
                self.field.fake_data(),
                {
                    'name': 'about_content',
                    'type': self._type,
                    'value': {
                        'blocks': [{
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': '1',
                            'text': 'abc',
                            'type': 'unstyled'
                        }, {
                            'data': {},
                            'depth': 0,
                            'entityRanges': [],
                            'inlineStyleRanges': [],
                            'key': '1',
                            'text': 'xyz',
                            'type': 'unstyled'
                        }],
                        'entityMap': {}
                    }
                })

    def test_to_internal_value(self):
        self.assertDictEqual(
            self.field.to_internal_value({'c': 'd'}),
            {
                'about_content_type': self._type,
                'about_content_value': {
                    'c': 'd'
                }
            })


class RichTestFieldTestCase(MultilineTextFieldTestCase):
    _type = 'rich_text'

    def setUp(self):
        self.field = RichTextField(fake_value=['abc', 'xyz'])
        self.field.field_name = 'about_content'


class RandomizerFieldTestCase(SimpleTestCase):
    def setUp(self):
        self.randomizer_field = RandomizerField()
        self.randomizer_field.field_name = 'faq_randomizer'

    def test_to_representation(self):
        self.assertDictEqual(
            self.randomizer_field.to_representation({
                'faq_randomizer_pool_size': 10,
                'faq_randomizer_selected_strategy_id': 1
            }),
            {
                'name': 'faq_randomizer',
                'type': 'randomizer',
                'value': {
                    'poolSize': 10,
                    'selectedStrategyId': 1,
                    'strategies': RANDOMIZER_STRATEGIES
                }
            })

    def test_fake_data(self):
        self.assertDictEqual(
            self.randomizer_field.fake_data(),
            {
                'name': 'faq_randomizer',
                'type': 'randomizer',
                'value': {
                    'poolSize': 10,
                    'selectedStrategyId': 1,
                    'strategies': RANDOMIZER_STRATEGIES
                }
            })

    def test_to_internal_value(self):
        self.assertDictEqual(
            self.randomizer_field.to_internal_value({
                'poolSize': 12,
                'selectedStrategyId': 2
            }),
            {
                'faq_randomizer_type': 'randomizer',
                'faq_randomizer_pool_size': 12,
                'faq_randomizer_selected_strategy_id': 2
            })
