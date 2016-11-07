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
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework import routers

from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailcore import urls as wagtail_urls

from story.views import StoryViewSet
from faq.views import FAQViewSet
from vftg.views import VFTGViewSet
from landing_page.views import LandingPageViewSet
from .views import index
from suggestion.views import SuggestionViewSet


router = routers.SimpleRouter()
router.register(r'stories', StoryViewSet, base_name='story')
router.register(r'faqs', FAQViewSet, base_name='faq')
router.register(r'vftg', VFTGViewSet, base_name='vftg')
router.register(r'landing-page', LandingPageViewSet, base_name='landing-page')
router.register(r'suggestion', SuggestionViewSet, base_name='suggestion')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^cms/', include(wagtailadmin_urls)),
    url(r'^wagtail/', include(wagtail_urls)),
    url(r'^api/v1/', include(router.urls, namespace='api')),
    url(r'^(?:(?P<path>collaborate|faq|reporting|search)/)?$', ensure_csrf_cookie(index), name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
