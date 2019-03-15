from django.contrib.sitemaps.views import sitemap, index
from django.urls import re_path

from sitemap.sitemaps.allegation_sitemap import AllegationSitemap
from sitemap.sitemaps.attachment_sitemap import AttachmentSitemap
from sitemap.sitemaps.officer_sitemap import OfficerSitemap
from sitemap.sitemaps.static_page_sitemap import StaticPageSiteMap
from sitemap.sitemaps.trr_sitemap import TRRSitemap
from sitemap.sitemaps.unit_sitemap import UnitSitemap

sitemaps = {
    'static_page': StaticPageSiteMap,
    'officer': OfficerSitemap,
    'allegation': AllegationSitemap,
    'trr': TRRSitemap,
    'unit': UnitSitemap,
    'attachment': AttachmentSitemap,
}

urlpatterns = [
    re_path(
        r'-(?P<section>\w+).xml$',
        sitemap,
        {'sitemaps': sitemaps},
        name='sitemaps',
    ),
    re_path(r'.xml$', index, {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps'}),
]
