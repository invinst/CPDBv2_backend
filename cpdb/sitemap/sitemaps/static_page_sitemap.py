from django.contrib.sitemaps import Sitemap


class StaticPageSiteMap(Sitemap):
    changefreq = 'daily'
    priority = 0.5

    def items(self):
        return ['', 'collaborate', 'terms']

    def location(self, item):
        return f'/{item}/' if item else ''
