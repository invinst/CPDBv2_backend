from data.constants import MEDIA_TYPE_DOCUMENT
from data.models import AttachmentFile
from sitemap.sitemaps.base_sitemap import BaseSitemap


class AttachmentSitemap(BaseSitemap):
    def items(self):
        return AttachmentFile.objects.showing().filter(file_type=MEDIA_TYPE_DOCUMENT).order_by('id')
