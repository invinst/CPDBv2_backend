from datetime import datetime

import pytz
from django.test import TestCase
from freezegun import freeze_time
from robber import expect

from data.factories import OfficerFactory
from sitemap.sitemaps.base_sitemap import BaseSitemap
from sitemap.sitemaps.officer_sitemap import OfficerSitemap


class OfficerSitemapTestCase(TestCase):
    def test_base(self):
        expect(issubclass(OfficerSitemap, BaseSitemap)).to.be.true()

    def test_items(self):
        OfficerFactory(id=123, allegation_count=2)
        OfficerFactory(id=456, allegation_count=3)
        OfficerFactory(id=789, allegation_count=1)

        items = list(OfficerSitemap().items())

        expect(items).to.have.length(3)
        expect(items[0].id).to.eq(456)
        expect(items[1].id).to.eq(123)
        expect(items[2].id).to.eq(789)

    def test_lastmod(self):
        officer = OfficerFactory(id=123)
        with freeze_time(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc)):
            officer.allegation_count = 2
            officer.save()

        officer.refresh_from_db()

        expect(OfficerSitemap().lastmod(officer)).to.eq(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc))
