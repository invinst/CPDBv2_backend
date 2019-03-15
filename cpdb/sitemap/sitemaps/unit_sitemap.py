from django.contrib.sitemaps import Sitemap

from data.models import PoliceUnit


class UnitSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.5

    def items(self):
        return PoliceUnit.objects.all()[:2]

    def lastmod(self, obj):
        return obj.updated_at
