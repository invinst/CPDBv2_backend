from django.test import TestCase
from robber import expect

from sitemap.sitemaps.base_sitemap import BaseSitemap
from sitemap.sitemaps.static_page_sitemap import StaticPageSiteMap


class StaticPageSiteMapTestCase(TestCase):
    def test_base(self):
        expect(issubclass(StaticPageSiteMap, BaseSitemap)).to.be.true()

    def test_items(self):
        expect(StaticPageSiteMap().items()).to.eq(['', 'collaborate', 'terms'])

    def test_location(self):
        expect(StaticPageSiteMap().location('collaborate')).to.eq('/collaborate/')
        expect(StaticPageSiteMap().location(None)).to.eq('')
