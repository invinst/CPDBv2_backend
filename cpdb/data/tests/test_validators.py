from django.core.exceptions import ValidationError
from django.test.testcases import SimpleTestCase
from robber import expect

from data.validators import validate_race


class ValidateRaceTestCase(SimpleTestCase):
    def test_invalid_value(self):
        expect(lambda: validate_race('nan')).to.throw(ValidationError)
        expect(lambda: validate_race('NAN')).to.throw(ValidationError)
        expect(lambda: validate_race('')).to.throw(ValidationError)

    def test_valid_value(self):
        expect(lambda: validate_race('Black')).not_to.throw(ValidationError)
        expect(lambda: validate_race('White')).not_to.throw(ValidationError)
        expect(lambda: validate_race('Unknown')).not_to.throw(ValidationError)
