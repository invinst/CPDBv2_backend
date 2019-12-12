from django.test.testcases import TestCase
from django.db.models import CharField

from robber import expect

from utils.models.choice_array_field import ChoiceArrayField


class ChoiceArrayFieldTestCase(TestCase):
    def test_formfield(self):
        choices = [
            ('CR', 'CR'),
            ('TRR', 'TRR'),
        ]
        base_field = CharField(max_length=20, choices=choices)
        custom_choice_array = ChoiceArrayField(base_field=base_field)
        expect(custom_choice_array.formfield()._choices).to.eq(choices)
