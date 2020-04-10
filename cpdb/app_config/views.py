from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from app_config.models import VisualTokenColor
from app_config.serializers import VisualTokenColorSerializer


class AppConfigViewSet(ViewSet):
    def list(self, request):
        visual_token_colors = VisualTokenColor.objects.order_by('lower_range')
        return Response({
            'visual_token_colors': VisualTokenColorSerializer(visual_token_colors, many=True).data,
        })
