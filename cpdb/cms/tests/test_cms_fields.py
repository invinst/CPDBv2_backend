from django.test import SimpleTestCase

from mock import Mock, patch
from freezegun import freeze_time

from cms.cms_fields import (
    LinkField, DateField, PlainTextField, MultilineTextField, RandomizerField, RandomizedListField)
from cms.randomizers import RANDOMIZER_STRATEGIES


class LinkFieldTestCase(SimpleTestCase):
    def setUp(self):
        self.link_field = LinkField(seed_value='http://google.com')
        self.descriptor = Mock()
        self.descriptor.get_field_value_from_model.return_value = 'http://google.com.vn'
        self.link_field.initialize('vftg_link')

    def test_to_representation(self):
        self.assertDictEqual(
            self.link_field.to_representation(self.descriptor),
            {
                'name': 'vftg_link',
                'type': 'link',
                'value': 'http://google.com.vn'
            })

    def test_seed_data(self):
        self.assertDictEqual(
            self.link_field.seed_data(),
            {
                'type': 'link',
                'value': 'http://google.com'
            })

    def test_to_internal_value(self):
        self.assertDictEqual(
            self.link_field.to_internal_value('http://abc.com'),
            {
                'type': 'link',
                'value': 'http://abc.com'
            })


class DateFieldTestCase(SimpleTestCase):
    def setUp(self):
        self.date_field = DateField()
        self.descriptor = Mock()
        self.descriptor.get_field_value_from_model.return_value = '2016-01-01'
        self.date_field.initialize('vftg_date')

    def test_to_representation(self):
        self.assertDictEqual(
            self.date_field.to_representation(self.descriptor),
            {
                'name': 'vftg_date',
                'type': 'date',
                'value': '2016-01-01'
            })

    @freeze_time('2012-01-14')
    def test_seed_data(self):
        self.assertDictEqual(
            self.date_field.seed_data(),
            {
                'type': 'date',
                'value': '2012-01-14'
            })

    def test_to_internal_value(self):
        self.assertDictEqual(
            self.date_field.to_internal_value('2016-06-06'),
            {
                'type': 'date',
                'value': '2016-06-06'
            })


class PlainTextFieldTestCase(SimpleTestCase):
    def setUp(self):
        self.plain_text_field = PlainTextField(seed_value='About')
        self.descriptor = Mock()
        self.descriptor.get_field_value_from_model.return_value = {'a': 'b'}
        self.plain_text_field.initialize('about_header')

    def test_to_representation(self):
        self.assertDictEqual(
            self.plain_text_field.to_representation(self.descriptor),
            {
                'name': 'about_header',
                'type': 'plain_text',
                'value': {
                    'a': 'b'
                }
            })

    def test_seed_data(self):
        with patch('cms.cms_fields.generate_draft_block_key', return_value='1'):
            self.assertDictEqual(
                self.plain_text_field.seed_data(),
                {
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
                'type': 'plain_text',
                'value': {
                    'c': 'd'
                }
            })


class MultilineTextFieldTestCase(SimpleTestCase):
    def setUp(self):
        self.multiline_text_field = MultilineTextField(seed_value=['abc', 'xyz'])
        self.descriptor = Mock()
        self.descriptor.get_field_value_from_model.return_value = {'a': 'b'}
        self.multiline_text_field.initialize('about_content')

    def test_to_representation(self):
        self.assertDictEqual(
            self.multiline_text_field.to_representation(self.descriptor),
            {
                'name': 'about_content',
                'type': 'multiline_text',
                'value': {
                    'a': 'b'
                }
            })

    def test_seed_data(self):
        with patch('cms.cms_fields.generate_draft_block_key', return_value='1'):
            self.assertDictEqual(
                self.multiline_text_field.seed_data(),
                {
                    'type': 'multiline_text',
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
            self.multiline_text_field.to_internal_value({'c': 'd'}),
            {
                'type': 'multiline_text',
                'value': {
                    'c': 'd'
                }
            })


class RandomizerFieldTestCase(SimpleTestCase):
    def setUp(self):
        self.randomizer_field = RandomizerField()

        def mock_get_field_value(name, suffix):
            if suffix == 'pool_size':
                return 10
            elif suffix == 'selected_strategy_id':
                return 1
        self.descriptor = Mock()
        self.descriptor.get_field_value_from_model = mock_get_field_value
        self.randomizer_field.initialize('faq_randomizer')

    def test_to_representation(self):
        self.assertDictEqual(
            self.randomizer_field.to_representation(self.descriptor),
            {
                'name': 'faq_randomizer',
                'type': 'randomizer',
                'value': {
                    'poolSize': 10,
                    'selectedStrategyId': 1,
                    'strategies': RANDOMIZER_STRATEGIES
                }
            })

    def test_seed_data(self):
        self.assertDictEqual(
            self.randomizer_field.seed_data(),
            {
                'type': 'randomizer',
                'pool_size': 10,
                'selected_strategy_id': 1
            })

    def test_to_internal_value(self):
        self.assertDictEqual(
            self.randomizer_field.to_internal_value({
                'poolSize': 12,
                'selectedStrategyId': 2
                }),
            {
                'type': 'randomizer',
                'pool_size': 12,
                'selected_strategy_id': 2
            })


class RandomizedListFieldTestCase(SimpleTestCase):
    def setUp(self):
        FAQ = Mock()
        FAQ.objects = Mock()
        self.faq_objects = FAQ.objects
        self.descriptor = Mock()
        self.descriptor.faq_randomizer = Mock()
        self.descriptor.faq_randomizer.value = {
            'pool_size': 10,
            'selected_strategy_id': 1
        }
        self.randomized_list_field = RandomizedListField(count=3, randomizer_field='faq_randomizer', model=FAQ)
        self.randomized_list_field.initialize('faqs')

    def test_to_representation(self):
        with patch('cms.cms_fields.randomize', return_value=['a', 'b', 'c']) as mock_function:
            self.assertDictEqual(
                self.randomized_list_field.to_representation(self.descriptor),
                {
                    'name': 'faqs',
                    'type': 'randomized_list',
                    'value': ['a', 'b', 'c']
                })
            mock_function.assert_called_with(self.faq_objects, 10, 3, 1)
