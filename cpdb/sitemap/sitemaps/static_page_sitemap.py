from sitemap.sitemaps.base_sitemap import BaseSitemap


class StaticPageSiteMap(BaseSitemap):
    def items(self):
        return ['', 'collaborate', 'terms']

    def location(self, item):
        return f'/{item}/' if item else ''

    def lastmod(self, obj):
        return None
