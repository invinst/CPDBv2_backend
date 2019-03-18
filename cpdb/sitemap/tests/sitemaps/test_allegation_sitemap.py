from datetime import datetime

from django.test import TestCase
from sitemap.sitemaps.allegation_sitemap import AllegationSitemap

from robber import expect
from freezegun import freeze_time
import pytz

from data.factories import AllegationFactory


class AllegationSitemapTestCase(TestCase):
    def test_class_properties(self):
        expect(AllegationSitemap.changefreq).to.eq('daily')
        expect(AllegationSitemap.priority).to.eq(0.5)

    def test_items(self):
        allegation_1 = AllegationFactory(crid='123', coaccused_count=2)
        allegation_2 = AllegationFactory(crid='456', coaccused_count=3)
        allegation_3 = AllegationFactory(crid='789', coaccused_count=1)

        items = list(AllegationSitemap().items())

        expect(items).to.have.length(3)
        expect(items[0]).to.eq(allegation_2)
        expect(items[1]).to.eq(allegation_1)
        expect(items[2]).to.eq(allegation_3)

    def test_lastmod(self):
        allegation = AllegationFactory(crid='123')
        with freeze_time(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc)):
            allegation.coaccused_count = 2
            allegation.save()

        allegation.refresh_from_db()

        expect(AllegationSitemap().lastmod(allegation)).to.eq(datetime(2018, 4, 4, 12, 0, 1, tzinfo=pytz.utc))
