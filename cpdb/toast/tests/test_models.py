from django.test.testcases import TestCase
from robber.expect import expect

from toast.factories import ToastFactory


class ToastTestCase(TestCase):
    def test_str_method(self):
        expect(str(ToastFactory(name='toast name'))).to.eq('toast name')
