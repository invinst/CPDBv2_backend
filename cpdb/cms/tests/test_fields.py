from django.test import SimpleTestCase

from mock import patch
from rest_framework import serializers
from freezegun import freeze_time

from cms.factories import LinkEntityFactory
from cms.fields import (
    LinkField, DateField, RichTextField, RandomizerField, StringField)
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

    def test_raise_validation_error(self):
        with self.assertRaises(serializers.ValidationError) as context_manager:
            self.string_field.to_internal_value(None)

        self.assertEqual(context_manager.exception.detail, {'vftg_title': 'Value is not string'})


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

    def test_raise_validation_error(self):
        with self.assertRaises(serializers.ValidationError) as context_manager:
            self.link_field.to_internal_value(None)

        self.assertEqual(context_manager.exception.detail, {'vftg_link': 'Value is not string'})


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

    def test_raise_validation_error(self):
        with self.assertRaises(serializers.ValidationError) as context_manager:
            self.date_field.to_internal_value('abc')

        self.assertEqual(context_manager.exception.detail, {
            'vftg_date': 'Value must be in valid date format: YYYY-MM-DD'
        })

    def test_fake_data_with_fake_value(self):
        self.date_field = DateField(fake_value='2016-11-09')
        self.date_field.field_name = 'vftg_date'
        self.assertDictEqual(
            self.date_field.fake_data(),
            {
                'name': 'vftg_date',
                'type': 'date',
                'value': '2016-11-09'
            })


class RichTestFieldTestCase(SimpleTestCase):
    _type = 'rich_text'

    def setUp(self):
        self.field = RichTextField(fake_value=['abc', 'xyz'])
        self.field.field_name = 'about_content'
        self.maxDiff = None

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
            self.field.to_internal_value({
                'blocks': 'c',
                'entityMap': 'd'
            }),
            {
                'about_content_type': self._type,
                'about_content_value': {
                    'blocks': 'c',
                    'entityMap': 'd'
                }
            })

    def test_raise_validation_error(self):
        with self.assertRaises(serializers.ValidationError) as context_manager:
            self.field.to_internal_value('abc')

        self.assertEqual(context_manager.exception.detail, {
            'about_content': 'Value must be in raw content state format'
        })

    def test_fake_data_with_value_object(self):
        value = {
            'blocks': ['abc'],
            'entities': [
                LinkEntityFactory(
                    url='url',
                    length=1,
                    offset=0,
                    block_index=0
                )
            ]
        }
        with patch('cms.fields.generate_draft_block_key', return_value='1'):
            self.assertDictEqual(
                self.field.fake_data(value),
                {
                    'name': 'about_content',
                    'type': self._type,
                    'value': {
                        'blocks': [{
                            'data': {},
                            'depth': 0,
                            'entityRanges': [{
                                'length': 1,
                                'key': 0,
                                'offset': 0
                            }],
                            'inlineStyleRanges': [],
                            'key': '1',
                            'text': 'abc',
                            'type': 'unstyled'
                        }],
                        'entityMap': {
                            0: {
                                'data': {'url': 'url'},
                                'type': 'LINK',
                                'mutability': 'MUTABLE'
                            }
                        }
                    }
                })


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

    def test_to_representation_return_none_when_data_is_invalid(self):
        self.assertIsNone(self.randomizer_field.to_representation({}))

    def test_raise_validation_error(self):
        with self.assertRaises(serializers.ValidationError) as context_manager:
            self.randomizer_field.to_internal_value({})

        self.assertEqual(context_manager.exception.detail, {
            'faq_randomizer': 'Value must contain both "poolSize" key and "selectedStrategyId" key.'
        })
