from data.models import PoliceUnit
from sitemap.sitemaps.base_sitemap import BaseSitemap


class UnitSitemap(BaseSitemap):
    def items(self):
        return PoliceUnit.objects.all().order_by('unit_name')
