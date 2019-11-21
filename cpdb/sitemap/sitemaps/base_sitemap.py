from django.contrib.sitemaps import Sitemap


class BaseSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.5
    protocol = 'https'

    def items(self):
        raise NotImplementedError

    def lastmod(self, obj):
        return obj.updated_at
