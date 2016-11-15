from rest_framework import viewsets
from rest_framework.response import Response

from landing_page.models import LandingPage
from landing_page.serializers import LandingPageSerializer


class LandingPageViewSet(viewsets.ViewSet):
    """
    View to list landing page content
    """
    def list(self, request, format=None):
        landing_page = LandingPage.objects.first()
        serializer = LandingPageSerializer(landing_page)
        return Response(serializer.data)
