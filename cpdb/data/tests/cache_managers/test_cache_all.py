from django.test.testcases import TestCase

from mock import patch
from robber import expect

from data import cache_managers


class CacheManagersTestCase(TestCase):
    @patch('data.cache_managers.allegation_cache_manager.cache_data')
    @patch('data.cache_managers.officer_cache_manager.cache_data')
    @patch('data.cache_managers.salary_cache_manager.cache_data')
    def test_cache_all(self, salary_cache_mock, officer_cache_mock, allegation_cache_mock):
        cache_managers.cache_all()
        expect(salary_cache_mock).to.be.called_once()
        expect(officer_cache_mock).to.be.called_once()
        expect(allegation_cache_mock).to.be.called_once()
        expect(len(cache_managers.managers)).to.eq(3)
