from django.test import TestCase
from sitemap.sitemaps.static_page_sitemap import StaticPageSiteMap

from robber import expect


class StaticPageSiteMapTestCase(TestCase):
    def test_class_properties(self):
        expect(StaticPageSiteMap.changefreq).to.eq('daily')
        expect(StaticPageSiteMap.priority).to.eq(0.5)

    def test_items(self):
        expect(StaticPageSiteMap().items()).to.eq(['', 'collaborate', 'terms'])

    def test_location(self):
        expect(StaticPageSiteMap().location('collaborate')).to.eq('/collaborate/')
        expect(StaticPageSiteMap().location(None)).to.eq('')
