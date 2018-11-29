from django.test.testcases import TestCase, override_settings
from django.core.management import call_command
from django.core.cache import cache

from robber import expect


class CacheDataTestCase(TestCase):
    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    })
    def test_cache(self):
        cache.set('abc', 'def')
        expect(cache.get('abc')).to.eq('def')
        call_command('clear_cache')
        expect(cache.get('abc')).to.eq(None)
