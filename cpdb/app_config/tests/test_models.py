from robber import expect
from django.test.testcases import TestCase
from django.core.exceptions import ValidationError

from app_config.factories import VisualTokenColorFactory


class VisualTokenColorModelTestCase(TestCase):
    def test_should_raise_error_on_invalid_lower_range(self):
        expect(VisualTokenColorFactory.create(lower_range=-1).full_clean).to.throw(ValidationError)
        expect(VisualTokenColorFactory.create(lower_range=101).full_clean).to.throw(ValidationError)

    def test_should_raise_error_on_invalid_upper_range(self):
        expect(VisualTokenColorFactory.create(upper_range=-1).full_clean).to.throw(ValidationError)
        expect(VisualTokenColorFactory.create(upper_range=101).full_clean).to.throw(ValidationError)

    def test_should_raise_error_on_invalid_color(self):
        expect(VisualTokenColorFactory.create(color='#12345').full_clean).to.throw(ValidationError)
        expect(VisualTokenColorFactory.create(color='#123g56').full_clean).to.throw(ValidationError)
        expect(VisualTokenColorFactory.create(color='123f56').full_clean).to.throw(ValidationError)

    def test_should_raise_error_on_invalid_text_color(self):
        expect(VisualTokenColorFactory.create(text_color='#12345').full_clean).to.throw(ValidationError)
        expect(VisualTokenColorFactory.create(text_color='#123g56').full_clean).to.throw(ValidationError)
        expect(VisualTokenColorFactory.create(text_color='123f56').full_clean).to.throw(ValidationError)

    def test_should_not_raise_error_on_valid_lower_range(self):
        expect(VisualTokenColorFactory.create(lower_range=0.3).full_clean).not_to.throw(ValidationError)
        expect(VisualTokenColorFactory.create(lower_range=99.9).full_clean).not_to.throw(ValidationError)

    def test_should_not_raise_error_on_valid_upper_range(self):
        expect(VisualTokenColorFactory.create(upper_range=0.3).full_clean).not_to.throw(ValidationError)
        expect(VisualTokenColorFactory.create(upper_range=99.9).full_clean).not_to.throw(ValidationError)

    def test_should_not_raise_error_on_valid_color(self):
        expect(VisualTokenColorFactory.create(color='#123456').full_clean).not_to.throw(ValidationError)
        expect(VisualTokenColorFactory.create(color='#a23f56').full_clean).not_to.throw(ValidationError)

    def test_should_not_raise_error_on_valid_text_color(self):
        expect(VisualTokenColorFactory.create(text_color='#123456').full_clean).not_to.throw(ValidationError)
        expect(VisualTokenColorFactory.create(text_color='#a23f56').full_clean).not_to.throw(ValidationError)
