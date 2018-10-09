from django.test.testcases import TestCase
from django.core.management import call_command

from mock import patch
from robber import expect


class CacheDataTestCase(TestCase):
    @patch('data.cache_managers.cache_all')
    def test_cache(self, cache_all_mock):
        call_command('cache_data')
        expect(cache_all_mock).to.be.called_once()
