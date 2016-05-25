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

from rest_framework import routers

from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailcore import urls as wagtail_urls

from example.views import ExampleAPIView
from story.views import StoryViewSet


router = routers.SimpleRouter()
router.register(r'stories', StoryViewSet, base_name='story')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^cms/', include(wagtailadmin_urls)),
    url(r'^wagtail/', include(wagtail_urls)),
    url(r'^api/hello-world/$', ExampleAPIView.as_view(), name='super-api'),
    url(r'^api/v1/', include(router.urls, namespace='api'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
