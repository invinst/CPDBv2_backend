from django.test import TestCase
from robber import expect

from data.factories import OfficerFactory, SalaryFactory
from data.models import Salary


class SalaryManagerTestCase(TestCase):
    def test_ranks(self):
        SalaryFactory(rank='Detective', officer__rank='Officer')
        SalaryFactory(rank='Officer', officer__rank='Officer')
        OfficerFactory(rank='Senior Police Officer')

        ranks = Salary.objects.ranks
        expect(ranks).to.eq(['Detective', 'Officer', 'Senior Police Officer'])
