from rest_framework import viewsets
from rest_framework.response import Response

from landing_page.models import LandingPage, LandingPageContent
from landing_page.serializers import LandingPageSerializer, LandingPageContentSerializer
from landing_page.deserializers import LandingPageContentDeserializer


class LandingPageViewSet(viewsets.ViewSet):
    """
    View to list landing page content
    """
    def list(self, request, format=None):
        landing_page = LandingPage.objects.first()
        serializer = LandingPageSerializer(landing_page)
        return Response(serializer.data)


class LandingPageContentViewSet(viewsets.ViewSet):
    def list(self, request, format=None):
        landing_page_content = LandingPageContent.objects.first()
        serializer = LandingPageContentSerializer(landing_page_content)
        return Response(serializer.data)

    def create(self, request):
        landing_page_content = LandingPageContent.objects.first()
        deserializer = LandingPageContentDeserializer(landing_page_content, data=request.data)
        deserializer.is_valid()
        deserializer.save()
        return Response(deserializer.data)
