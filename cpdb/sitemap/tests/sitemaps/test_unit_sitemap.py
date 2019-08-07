from datetime import datetime

from django.test import TestCase

from robber import expect
from freezegun import freeze_time
import pytz

from data.factories import PoliceUnitFactory
from sitemap.sitemaps.unit_sitemap import UnitSitemap


class UnitSiteMapTestCase(TestCase):
    def test_class_properties(self):
        expect(UnitSitemap.changefreq).to.eq('daily')
        expect(UnitSitemap.priority).to.eq(0.5)

    def test_items(self):
        unit_1 = PoliceUnitFactory(id=123, unit_name='002')
        unit_2 = PoliceUnitFactory(id=789, unit_name='001')
        unit_3 = PoliceUnitFactory(id=456, unit_name='003')

        items = list(UnitSitemap().items())

        expect(items).to.have.length(3)
        expect(items[0]).to.eq(unit_2)
        expect(items[1]).to.eq(unit_1)
        expect(items[2]).to.eq(unit_3)

    def test_lastmod(self):
        unit = PoliceUnitFactory(id=123, description='old description')
        with freeze_time(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc)):
            unit.description = 'new description'
            unit.save()

        unit.refresh_from_db()

        expect(UnitSitemap().lastmod(unit)).to.eq(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc))
