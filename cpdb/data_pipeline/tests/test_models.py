from django.test import TestCase

from robber import expect

from data_pipeline.models import AppliedFixture


class AppliedFixtureTextCase(TestCase):
    def test_unicode(self):
        fixture = AppliedFixture(file_name='123_abc.json')
        expect(str(fixture)).to.eq('123_abc.json')
