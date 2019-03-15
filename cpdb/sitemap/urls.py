from django.contrib.sitemaps.views import sitemap
from django.urls import re_path

from sitemap.sitemaps.officer_sitemap import OfficerSitemap

urlpatterns = [
    re_path(
        '^$',
        sitemap,
        {
            'sitemaps':
            {
                'officer': OfficerSitemap
            },
        },
        name='django.contrib.sitemaps.views.sitemap'
    ),
]
