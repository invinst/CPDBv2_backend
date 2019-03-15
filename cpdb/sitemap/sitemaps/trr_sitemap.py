from django.contrib.sitemaps import Sitemap

from trr.models import TRR


class TRRSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.5

    def items(self):
        return TRR.objects.all()[:2]

    def lastmod(self, obj):
        return obj.updated_at
