from datetime import date

from django.test.testcases import TestCase

from robber import expect

from data.cache_managers import salary_cache_manager
from data.factories import (
    OfficerFactory, SalaryFactory)
from data.models import Salary


class SalaryCacheManagerTestCase(TestCase):
    def test_cache_data(self):
        officer_1 = OfficerFactory(appointed_date=date(2005, 1, 1))
        officer_2 = OfficerFactory(appointed_date=date(2005, 1, 1))
        officer_1_salary_1 = SalaryFactory(
            officer=officer_1, salary=5000, year=2005, rank='Police Officer', spp_date=date(2005, 1, 1),
        )
        SalaryFactory(
            officer=officer_1, salary=10000, year=2006, rank='Police Officer', spp_date=date(2005, 1, 1),
        )
        SalaryFactory(
            officer=officer_1, salary=10000, year=2006, rank='Police Officer', spp_date=None,
        )
        officer_1_salary_2 = SalaryFactory(
            officer=officer_1, salary=15000, year=2007, rank='Sergeant', spp_date=date(2007, 1, 1),
        )
        officer_2_salary_1 = SalaryFactory(
            officer=officer_2, salary=5000, year=2005, rank='Police Officer', spp_date=date(2005, 1, 1),
        )
        officer_2_salary_2 = SalaryFactory(
            officer=officer_2, salary=15000, year=2006, rank='Detective', spp_date=date(2006, 1, 1),
        )
        SalaryFactory(
            officer=officer_2, salary=20000, year=2007, rank='Detective', spp_date=date(2006, 1, 1),
        )
        salary_cache_manager.cache_data()

        rank_changed_salary_ids = set(s.id for s in Salary.objects.filter(rank_changed=True))
        expected_rank_changed_salary_ids = {
            officer_1_salary_1.id, officer_1_salary_2.id, officer_2_salary_1.id, officer_2_salary_2.id
        }
        expect(rank_changed_salary_ids).to.eq(expected_rank_changed_salary_ids)
