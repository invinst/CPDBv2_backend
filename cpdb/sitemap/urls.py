from django.contrib.sitemaps.views import sitemap
from django.urls import re_path

from sitemap.sitemaps.allegation_sitemap import AllegationSitemap
from sitemap.sitemaps.attachment_sitemap import AttachmentSitemap
from sitemap.sitemaps.officer_sitemap import OfficerSitemap
from sitemap.sitemaps.trr_sitemap import TRRSitemap
from sitemap.sitemaps.unit_sitemap import UnitSitemap

urlpatterns = [
    re_path(
        '^$',
        sitemap,
        {
            'sitemaps':
            {
                'officer': OfficerSitemap,
                'allegation': AllegationSitemap,
                'trr': TRRSitemap,
                'unit': UnitSitemap,
                'attachment': AttachmentSitemap,
            },
        },
        name='django.contrib.sitemaps.views.sitemap'
    ),
]
