from datetime import datetime

from django.test import TestCase

from robber import expect
import pytz

from shared.tests.utils import create_object
from sitemap.sitemaps.base_sitemap import BaseSitemap


class DummySitemap(BaseSitemap):
    def items(self):
        return ['first', 'second', 'third']


class NoItemsSitemap(BaseSitemap):
    pass


class BaseMapTestCase(TestCase):
    def test_class_properties(self):
        expect(DummySitemap.changefreq).to.eq('daily')
        expect(DummySitemap.priority).to.eq(0.5)
        expect(DummySitemap.protocol).to.eq('https')

    def test_items(self):
        expect(DummySitemap().items()).to.eq(['first', 'second', 'third'])
        expect(NoItemsSitemap().items).to.throw(NotImplementedError)

    def test_lastmod(self):
        dummy_obj = create_object({'id': 1, 'updated_at': datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc)})
        expect(DummySitemap().lastmod(dummy_obj)).to.eq(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc))
