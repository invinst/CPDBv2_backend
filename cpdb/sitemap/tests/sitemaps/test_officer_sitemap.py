from datetime import datetime

from django.test import TestCase
from sitemap.sitemaps.officer_sitemap import OfficerSitemap

from robber import expect
from freezegun import freeze_time
import pytz

from data.factories import OfficerFactory


class OfficerSitemapTestCase(TestCase):
    def test_class_properties(self):
        expect(OfficerSitemap.changefreq).to.eq('daily')
        expect(OfficerSitemap.priority).to.eq(0.5)

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
