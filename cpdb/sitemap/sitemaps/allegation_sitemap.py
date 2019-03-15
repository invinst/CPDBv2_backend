from django.contrib.sitemaps import Sitemap

from data.models import Allegation


class AllegationSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.5

    def items(self):
        return Allegation.objects.all()[:2]

    def lastmod(self, obj):
        return obj.updated_at
