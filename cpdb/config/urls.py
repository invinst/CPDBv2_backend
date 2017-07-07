"""cpdb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework import routers

from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailcore import urls as wagtail_urls

from vftg.views import VFTGViewSet
from .views import index
from story.views import StoryViewSet
from faq.views import FAQViewSet
from landing_page.views import LandingPageViewSet
from search.views import SearchV2ViewSet, SearchV1ViewSet
from search_mobile.views import SearchMobileV2ViewSet
from authentication.views import UserViewSet
from cms.views import CMSPageViewSet, ReportPageViewSet, FAQPageViewSet
from report_bottomsheet.views import ReportBottomSheetOfficerSearchViewSet
from officers.views import OfficersViewSet
from analytics.views import EventViewSet, SearchTrackingViewSet
from cr.views import CRViewSet
from units.views import UnitsViewSet


router_v1 = routers.SimpleRouter()
router_v1.register(r'vftg', VFTGViewSet, base_name='vftg')
router_v1.register(r'stories', StoryViewSet, base_name='story')
router_v1.register(r'faqs', FAQViewSet, base_name='faq')
router_v1.register(r'landing-page', LandingPageViewSet, base_name='landing-page')
router_v1.register(r'suggestion', SearchV1ViewSet, base_name='suggestion')

router_v2 = routers.SimpleRouter()
router_v2.register(r'cms-pages', CMSPageViewSet, base_name='cms-page')
router_v2.register(r'reports', ReportPageViewSet, base_name='report')
router_v2.register(r'faqs', FAQPageViewSet, base_name='faq')
router_v2.register(r'users', UserViewSet, base_name='user')
router_v2.register(r'events', EventViewSet, base_name='event')
router_v2.register(r'search', SearchV2ViewSet, base_name='search')
router_v2.register(r'search-mobile', SearchMobileV2ViewSet, base_name='search-mobile')
router_v2.register(
    r'report-bottomsheet-officer-search',
    ReportBottomSheetOfficerSearchViewSet,
    base_name='report-bottomsheet-officer-search')
router_v2.register(r'officers', OfficersViewSet, base_name='officers')
router_v2.register(r'cr', CRViewSet, base_name='cr')
router_v2.register(r'search-tracking', SearchTrackingViewSet, base_name='search-tracking')
router_v2.register(r'units', UnitsViewSet, base_name='units')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^cms/', include(wagtailadmin_urls)),
    url(r'^wagtail/', include(wagtail_urls)),
    url(r'^api/v1/', include(router_v1.urls, namespace='api')),
    url(r'^api/v2/', include(router_v2.urls, namespace='api-v2')),
    url(r'^(?:(?P<path>'
        r'collaborate|faq(/\d+)?|reporting(/\d+)?|search|'
        r'resolving(?:/(?:officer-matching|officer-merging|dedupe-training|search-tracking)?)?|'
        r'officer/\d+(?:/timeline)?|'
        r'unit/\d+|'
        r'complaint/\d+/\d+|'
        r'edit(?:/(?:reporting|faq)(?:/\d+)?)?'
        r')/)?$', ensure_csrf_cookie(index), name='index'),
    url(r'^reset-password-confirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset-password-complete/$', auth_views.password_reset_complete, name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
