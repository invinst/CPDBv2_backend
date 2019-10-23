from data.models import Officer
from sitemap.sitemaps.base_sitemap import BaseSitemap


class OfficerSitemap(BaseSitemap):
    def items(self):
        return Officer.objects.all().order_by('-allegation_count')
