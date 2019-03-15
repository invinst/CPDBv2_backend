from django.contrib.sitemaps import Sitemap

from data.models import Officer


class OfficerSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.5

    def items(self):
        return Officer.objects.all().order_by('-allegation_count')

    def lastmod(self, obj):
        return obj.updated_at
