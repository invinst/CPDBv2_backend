from sitemap.sitemaps.base_sitemap import BaseSitemap
from trr.models import TRR


class TRRSitemap(BaseSitemap):
    def items(self):
        return TRR.objects.all().order_by('id')
