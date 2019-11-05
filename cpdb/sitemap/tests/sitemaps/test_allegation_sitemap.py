from datetime import datetime

import pytz
from django.test import TestCase
from freezegun import freeze_time
from robber import expect

from data.factories import AllegationFactory
from sitemap.sitemaps.allegation_sitemap import AllegationSitemap
from sitemap.sitemaps.base_sitemap import BaseSitemap


class AllegationSitemapTestCase(TestCase):
    def test_base(self):
        expect(issubclass(AllegationSitemap, BaseSitemap)).to.be.true()

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
