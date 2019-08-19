from robber import expect
from django.test import TestCase

from search.tests.utils import IndexMixin
from shared.utils import formatted_errors


class SharedUtilsTestCase(IndexMixin, TestCase):
    def test_formatted_errors(self):
        errors = {'field_name': {0: ['Error 1.'], 1: ['Error 2.']}}
        expect(formatted_errors(errors)).to.eq({'field_name': ['Error 1.', 'Error 2.']})
