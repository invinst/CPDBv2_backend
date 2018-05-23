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

from trr.views import TRRViewSet
from vftg.views import VFTGViewSet
from .views import index_view, officer_view, complaint_view
from search.views import SearchV2ViewSet, SearchV1ViewSet
from search_mobile.views import SearchMobileV2ViewSet
from authentication.views import UserViewSet
from cms.views import CMSPageViewSet
from officers.views import OfficersViewSet
from analytics.views import EventViewSet, SearchTrackingViewSet
from cr.views import CRViewSet, CRMobileViewSet
from units.views import UnitsViewSet
from alias.views import AliasViewSet
from visual_token.views import VisualTokenView
from activity_grid.views import ActivityGridViewSet
from search_terms.views import SearchTermCategoryViewSet
from heatmap.views import CitySummaryViewSet


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
router_v2.register(r'officers', OfficersViewSet, base_name='officers')
router_v2.register(r'cr', CRViewSet, base_name='cr')
router_v2.register(r'trr', TRRViewSet, base_name='trr')
router_v2.register(r'mobile/cr', CRMobileViewSet, base_name='cr-mobile')
router_v2.register(r'search-tracking', SearchTrackingViewSet, base_name='search-tracking')
router_v2.register(r'units', UnitsViewSet, base_name='units')
router_v2.register(r'activity-grid', ActivityGridViewSet, base_name='activity-grid')
router_v2.register(r'search-term-categories', SearchTermCategoryViewSet, base_name='search-term-categories')
router_v2.register(r'city-summary', CitySummaryViewSet, base_name='city-summary')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/', include(router_v1.urls, namespace='api')),
    url(r'^api/v2/', include(router_v2.urls, namespace='api-v2')),
    url(r'^(?:(?P<path>'
        r'collaborate|search(?:/terms)?|'
        r'resolving(?:/(?:officer-matching|officer-merging|dedupe-training|search-tracking)?)?|'
        r'unit/\d+|'
        r'edit(?:/(?:search(?:/alias(?:/form)?)?)(?:/\d+)?)?'
        r')/)?$', ensure_csrf_cookie(index_view), name='index'),
    url(
        r'^officer/(?P<officer_id>\d+)(?P<subpath>/(?:timeline|social))?/$',
        ensure_csrf_cookie(officer_view), name='officer'),
    url(r'^complaint/(?P<crid>\d+)(?:/(?P<officer_id>\d+))?/$', ensure_csrf_cookie(complaint_view), name='complaint'),
    url(r'^reset-password-confirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset-password-complete/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^visual-token/(?P<renderer>[\w\.]+)/$', VisualTokenView.as_view(), name='visual_token'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
