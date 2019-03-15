from django.contrib.sitemaps import Sitemap

from data.models import Officer


class OfficerSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.5

    def items(self):
        return Officer.objects.all()[:10]

    def lastmod(self, obj):
        return obj.updated_at
