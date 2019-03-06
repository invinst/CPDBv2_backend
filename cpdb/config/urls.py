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
from django.urls import re_path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

from rest_framework import routers

from popup.views import PopupViewSet
from trr.views import TRRDesktopViewSet, TRRMobileViewSet
from vftg.views import VFTGViewSet
from search.views import SearchV2ViewSet, SearchV1ViewSet
from search_mobile.views import SearchMobileV2ViewSet
from authentication.views import UserViewSet
from cms.views import CMSPageViewSet
from officers.views import OfficersDesktopViewSet, OfficersMobileViewSet
from analytics.views import EventViewSet, SearchTrackingViewSet, AttachmentTrackingViewSet
from cr.views import CRViewSet, CRMobileViewSet
from units.views import UnitsViewSet
from alias.views import AliasViewSet
from activity_grid.views import ActivityGridViewSet
from search_terms.views import SearchTermCategoryViewSet
from heatmap.views import CitySummaryViewSet
from twitterbot.views import WebhookViewSet
from status.views import StatusViewSet
from social_graph.views import SocialGraphViewSet
from tracker.views import AttachmentViewSet
from tracker.views import DocumentCrawlersViewSet


router_v1 = routers.SimpleRouter()
router_v1.register(r'vftg', VFTGViewSet, base_name='vftg')
router_v1.register(r'suggestion', SearchV1ViewSet, base_name='suggestion')

router_v2 = routers.SimpleRouter()
router_v2.register(r'cms-pages', CMSPageViewSet, base_name='cms-page')
router_v2.register(r'users', UserViewSet, base_name='user')
router_v2.register(r'events', EventViewSet, base_name='event')
router_v2.register(r'search', SearchV2ViewSet, base_name='search')
router_v2.register(r'aliases/(?P<alias_type>.+)', AliasViewSet, base_name='alias')
router_v2.register(r'search-mobile', SearchMobileV2ViewSet, base_name='search-mobile')
router_v2.register(r'officers', OfficersDesktopViewSet, base_name='officers')
router_v2.register(r'mobile/officers', OfficersMobileViewSet, base_name='officers-mobile')
router_v2.register(r'cr', CRViewSet, base_name='cr')
router_v2.register(r'mobile/cr', CRMobileViewSet, base_name='cr-mobile')
router_v2.register(r'trr', TRRDesktopViewSet, base_name='trr')
router_v2.register(r'mobile/trr', TRRMobileViewSet, base_name='trr-mobile')
router_v2.register(r'search-tracking', SearchTrackingViewSet, base_name='search-tracking')
router_v2.register(r'units', UnitsViewSet, base_name='units')
router_v2.register(r'activity-grid', ActivityGridViewSet, base_name='activity-grid')
router_v2.register(r'search-term-categories', SearchTermCategoryViewSet, base_name='search-term-categories')
router_v2.register(r'city-summary', CitySummaryViewSet, base_name='city-summary')
router_v2.register(r'popup', PopupViewSet, base_name='popup')
router_v2.register(r'twitter/webhook', WebhookViewSet, base_name='twitter-webhook')
router_v2.register(r'status', StatusViewSet, base_name='status')
router_v2.register(r'social-graph', SocialGraphViewSet, base_name='social-graph')
router_v2.register(r'attachment-tracking', AttachmentTrackingViewSet, base_name='attachment-tracking')
router_v2.register(r'attachments', AttachmentViewSet, base_name='attachments')
router_v2.register(r'document-crawlers', DocumentCrawlersViewSet, base_name='document-crawlers')

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    # The index_redirect url is redirecting 'admin' without slash too, we need to manually do this.
    re_path(r'^admin$', RedirectView.as_view(url='/admin/', permanent=True), name='admin_redirect'),
    re_path(r'^api/v1/', include((router_v1.urls, 'api'), namespace='api')),
    re_path(r'^api/v2/', include((router_v2.urls, 'api-v2'), namespace='api-v2')),
    re_path(
        r'^reset-password-confirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    re_path(
        r'^reset-password-complete/$',
        auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    re_path(r'^.+$', RedirectView.as_view(url='/', permanent=True), name='index_redirect')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar
    urlpatterns = [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
