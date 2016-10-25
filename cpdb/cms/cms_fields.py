from datetime import datetime
from faker import Faker

from cms.utils import generate_draft_block_key
from cms.randomizers import randomize, RANDOMIZER_STRATEGIES

fake = Faker()


class BaseField(object):
    virtual = False

    def to_representation(self, descriptor):
        return {
            'name': self.name,
            'type': self._type,
            'value': self.value(descriptor)
        }

    def initialize(self, name):
        self.name = name

    def to_internal_value(self, validated_data):
        return {
            'type': self._type,
            'value': validated_data
        }

    def value(self, descriptor):
        return descriptor.get_field_value_from_model(self.name, 'value')


class DraftEditorField(BaseField):
    def __init__(self, seed_value=None):
        self._seed_value = seed_value

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
    _type = 'string'

    def __init__(self, seed_value=None):
        self._seed_value = seed_value

    @property
    def seed_value(self):
        if self._seed_value is None:
            return fake.word()
        return self._seed_value

    def seed_data(self):
        return {
            'type': self._type,
            'value': self.seed_value
        }


class LinkField(StringField):
    _type = 'link'

    @property
    def seed_value(self):
        if self._seed_value is None:
            return fake.url()
        return self._seed_value


class DateField(BaseField):
    _type = 'date'

    def seed_data(self):
        return {
            'type': self._type,
            'value': datetime.now().strftime('%Y-%m-%d')
        }


class PlainTextField(DraftEditorField):
    _type = 'plain_text'

    @property
    def seed_value(self):
        if self._seed_value is None:
            return fake.sentence()
        return self._seed_value

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

    @property
    def seed_value(self):
        if self._seed_value is None:
            return fake.paragraphs(nb=2)
        return self._seed_value

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

    def value(self, descriptor):
        return {
            'poolSize': descriptor.get_field_value_from_model(self.name, 'pool_size'),
            'selectedStrategyId': descriptor.get_field_value_from_model(self.name, 'selected_strategy_id'),
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

    def __init__(self, count, randomizer_field, model, serializer_class, descriptor_class):
        self.count = count
        self.randomizer_field = randomizer_field
        self.model = model
        self.serializer_class = serializer_class
        self.descriptor_class = descriptor_class

    _type = 'randomized_list'

    def value(self, descriptor):
        strategy_field = getattr(descriptor, self.randomizer_field)
        randomizer = strategy_field.value(descriptor)

        instances = randomize(
            self.model.objects, randomizer['poolSize'], self.count,
            randomizer['selectedStrategyId'])

        serializer = self.serializer_class([self.descriptor_class(inst) for inst in instances], many=True)
        return serializer.data
