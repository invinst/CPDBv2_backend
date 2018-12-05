from datetime import datetime

from rest_framework import serializers
from faker import Faker

from cms.utils import generate_draft_block_key


class BaseCMSField(serializers.Field):
    def __init__(self, fake_value=None, *args, **kwargs):
        super(BaseCMSField, self).__init__(*args, **kwargs)
        self._fake_value = fake_value

    def to_representation(self, fields):
        try:
            return {
                'name': self.field_name,
                'type': self._type,
                'value': fields['%s_value' % self.field_name]
            }
        except KeyError:
            return None

    def to_internal_value(self, data):
        self.validate_value(data)
        return {
            '%s_type' % self.field_name: self._type,
            '%s_value' % self.field_name: data
        }


class StringField(BaseCMSField):
    _type = 'string'

    def fake_value(self, value=None):
        if value is not None:
            return value
        if self._fake_value is None:
            return Faker().word()
        return self._fake_value

    def fake_data(self, value=None):
        return {
            'name': self.field_name,
            'type': self._type,
            'value': self.fake_value(value)
        }

    def validate_value(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError({self.field_name: 'Value is not string'})


class LinkField(StringField):
    _type = 'link'

    def fake_value(self, value=None):
        if value is not None:
            return value
        if self._fake_value is None:
            return Faker().url()
        return self._fake_value


class DateField(StringField):
    _type = 'date'

    def fake_value(self, value=None):
        if value is not None:
            return value
        if self._fake_value is None:
            return datetime.now().strftime('%Y-%m-%d')
        return self._fake_value

    def validate_value(self, value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise serializers.ValidationError({self.field_name: 'Value must be in valid date format: YYYY-MM-DD'})


class DraftEditorField(BaseCMSField):
    def fake_block(self, value):
        return {
            'data': {},
            'depth': 0,
            'entityRanges': [],
            'inlineStyleRanges': [],
            'key': generate_draft_block_key(),
            'text': value,
            'type': 'unstyled'
        }

    def validate_value(self, value):
        if not ('blocks' in value and 'entityMap' in value):
            raise serializers.ValidationError({self.field_name: 'Value must be in raw content state format'})


class RichTextField(DraftEditorField):
    _type = 'rich_text'

    def fake_value(self, value=None):
        if value is not None:
            if isinstance(value, str):
                value = [value]
            return value
        if self._fake_value is None:
            return [Faker().sentence()]
        return self._fake_value

    def fake_data(self, value=None):
        if not value or 'blocks' not in value:
            blocks = [
                self.fake_block(val) for val in self.fake_value(value)
            ]
        else:
            blocks = [
                self.fake_block(text) for text in value['blocks']
            ]

        entitiesMap = dict()
        if value and 'entities' in value:
            for ind, entity in enumerate(value['entities']):
                entitiesMap[ind] = {
                    'data': entity.data,
                    'type': entity.type,
                    'mutability': entity.mutability
                }
                block = blocks[entity.block_index]
                block['entityRanges'].append({
                    'length': entity.length,
                    'key': ind,
                    'offset': entity.offset
                })

        return {
            'name': self.field_name,
            'type': self._type,
            'value': {
                'blocks': blocks,
                'entityMap': entitiesMap
            }
        }
