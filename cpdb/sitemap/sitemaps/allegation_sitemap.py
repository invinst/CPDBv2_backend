from data.models import Allegation
from sitemap.sitemaps.base_sitemap import BaseSitemap


class AllegationSitemap(BaseSitemap):
    def items(self):
        return Allegation.objects.all().order_by('-coaccused_count')
