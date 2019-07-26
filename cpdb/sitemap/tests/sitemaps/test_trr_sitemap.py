from datetime import datetime

import pytz
from django.test import TestCase
from freezegun import freeze_time
from robber import expect

from sitemap.sitemaps.trr_sitemap import TRRSitemap
from trr.factories import TRRFactory


class TRRSitemapTestCase(TestCase):
    def test_class_properties(self):
        expect(TRRSitemap.changefreq).to.eq('daily')
        expect(TRRSitemap.priority).to.eq(0.5)

    def test_items(self):
        trr_1 = TRRFactory(id=123)
        trr_2 = TRRFactory(id=789)
        trr_3 = TRRFactory(id=456)

        items = list(TRRSitemap().items())

        expect(items).to.have.length(3)
        expect(items[0]).to.eq(trr_1)
        expect(items[1]).to.eq(trr_3)
        expect(items[2]).to.eq(trr_2)

    def test_lastmod(self):
        trr = TRRFactory(id=123, beat=1)
        with freeze_time(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc)):
            trr.beat = 2
            trr.save()

        trr.refresh_from_db()

        expect(TRRSitemap().lastmod(trr)).to.eq(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc))
