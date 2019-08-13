from django.contrib.sitemaps import Sitemap

from data.constants import MEDIA_TYPE_DOCUMENT
from data.models import AttachmentFile


class AttachmentSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.5

    def items(self):
        return AttachmentFile.showing.filter(file_type=MEDIA_TYPE_DOCUMENT).order_by('id')

    def lastmod(self, obj):
        return obj.updated_at
