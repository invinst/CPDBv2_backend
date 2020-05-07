from robber import expect
from django.test.testcases import TestCase
from django.core.exceptions import ValidationError

from app_config.validators import is_valid_hex_color


class AppConfigValidatorTestCase(TestCase):
    def test_should_raise_error_on_short_hex_color(self):
        expect(lambda: is_valid_hex_color('#123')).to.throw(ValidationError)

    def test_should_raise_error_on_color_not_start_with_hash(self):
        expect(lambda: is_valid_hex_color('123f32')).to.throw(ValidationError)

    def test_should_raise_error_on_color_have_invalid_hex_character(self):
        expect(lambda: is_valid_hex_color('#123g32')).to.throw(ValidationError)

    def test_should_not_raise_error_on_valid_hex_color(self):
        expect(lambda: is_valid_hex_color('#123f32')).not_to.throw(ValidationError)
