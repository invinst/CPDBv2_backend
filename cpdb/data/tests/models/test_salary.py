from datetime import date

from django.test import TestCase
from robber import expect

from data.factories import OfficerFactory, SalaryFactory
from data.models import Salary


class SalaryManagerTestCase(TestCase):
    def test_rank_histories_without_joined(self):
        officer1 = OfficerFactory(appointed_date=date(2005, 1, 1))
        officer2 = OfficerFactory(appointed_date=date(2005, 1, 1))
        SalaryFactory(
            officer=officer1, salary=5000, year=2005, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer1, salary=10000, year=2006, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer1, salary=10000, year=2006, rank='Police Officer', spp_date=None,
            start_date=date(2005, 1, 1)
        )
        salary1 = SalaryFactory(
            officer=officer1, salary=15000, year=2007, rank='Sergeant', spp_date=date(2007, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer2, salary=5000, year=2005, rank='Police Officer', spp_date=date(2005, 1, 1),
            start_date=date(2005, 1, 1)
        )
        salary2 = SalaryFactory(
            officer=officer2, salary=15000, year=2006, rank='Detective', spp_date=date(2006, 1, 1),
            start_date=date(2005, 1, 1)
        )
        SalaryFactory(
            officer=officer2, salary=20000, year=2007, rank='Detective', spp_date=date(2006, 1, 1),
            start_date=date(2005, 1, 1)
        )
        expect(Salary.objects.rank_histories_without_joined()).to.eq([salary1, salary2])
