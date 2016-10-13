from datetime import datetime

from cms.utils import generate_draft_block_key
from cms.randomizers import randomize, RANDOMIZER_STRATEGIES


class BaseField(object):
    virtual = False

    def to_representation(self):
        return {
            'name': self.name,
            'type': self._type,
            'value': self.value
        }

    def initialize(self, name, descriptor):
        self.name = name
        self.descriptor = descriptor

    def to_internal_value(self, validated_data):
        return {
            'type': self._type,
            'value': validated_data
        }

    @property
    def value(self):
        return self.descriptor.get_field_value_from_model(self.name, 'value')


class DraftEditorField(BaseField):
    def get_key(self):
        return generate_draft_block_key()

    def get_seed_block(self, value):
        return {
            'data': {},
            'depth': 0,
            'entityRanges': [],
            'inlineStyleRanges': [],
            'key': self.get_key(),
            'text': value,
            'type': 'unstyled'
        }


class StringField(BaseField):
    def __init__(self, seed_value=''):
        self.seed_value = seed_value

    def seed_data(self):
        return {
            'type': self._type,
            'value': self.seed_value
        }


class LinkField(StringField):
    _type = 'link'


class DateField(BaseField):
    _type = 'date'

    def seed_data(self):
        return {
            'type': self._type,
            'value': datetime.now().strftime('%Y-%m-%d')
        }


class PlainTextField(DraftEditorField):
    _type = 'plain_text'

    def __init__(self, seed_value):
        self.seed_value = seed_value

    def seed_data(self):
        return {
            'type': self._type,
            'value': {
                'blocks': [
                    self.get_seed_block(self.seed_value)
                ],
                'entityMap': {}
            }
        }


class MultilineTextField(DraftEditorField):
    _type = 'multiline_text'

    def __init__(self, seed_value):
        self.seed_value = seed_value

    def seed_data(self):
        return {
            'type': self._type,
            'value': {
                'blocks': [
                    self.get_seed_block(value) for value in self.seed_value
                ],
                'entityMap': {}
            }
        }


class RandomizerField(BaseField):
    _type = 'randomizer'

    @property
    def value(self):
        return {
            'poolSize': self.descriptor.get_field_value_from_model(self.name, 'pool_size'),
            'selectedStrategyId': self.descriptor.get_field_value_from_model(self.name, 'selected_strategy_id'),
            'strategies': RANDOMIZER_STRATEGIES
        }

    def seed_data(self):
        return {
            'type': self._type,
            'pool_size': 10,
            'selected_strategy_id': 1
        }

    def to_internal_value(self, validated_data):
        return {
            'type': self._type,
            'pool_size': validated_data['poolSize'],
            'selected_strategy_id': validated_data['selectedStrategyId']
        }


class RandomizedListField(BaseField):
    virtual = True

    def __init__(self, count, randomizer_field, model):
        self.count = count
        self.randomizer_field = randomizer_field
        self.model = model

    _type = 'randomized_list'

    @property
    def value(self):
        strategy_field = getattr(self.descriptor, self.randomizer_field)
        randomizer = strategy_field.value

        return randomize(
            self.model.objects, randomizer['pool_size'], self.count,
            randomizer['selected_strategy_id'])
