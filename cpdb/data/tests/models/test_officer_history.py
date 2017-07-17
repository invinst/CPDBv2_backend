from django.test.testcases import TestCase

from robber.expect import expect

from data.factories import OfficerHistoryFactory, PoliceUnitFactory


class OfficerHistoryTestCase(TestCase):
    def test_unit_name(self):
        history = OfficerHistoryFactory(unit=PoliceUnitFactory(unit_name='abc'))
        expect(history.unit_name).to.eq('abc')
