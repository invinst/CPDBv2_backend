from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from app_config.models import AppConfig, VisualTokenColor
from app_config.serializers import VisualTokenColorSerializer
from app_config.constants import VISUAL_TOKEN_COLORS_KEY


class AppConfigViewSet(ViewSet):
    def list(self, request):
        app_config = AppConfig.objects.all()
        visual_token_colors = VisualTokenColor.objects.order_by('lower_range')
        config_data = {}
        for config_object in app_config:
            config_data[config_object.name] = config_object.value
        config_data[VISUAL_TOKEN_COLORS_KEY] = VisualTokenColorSerializer(visual_token_colors, many=True).data
        return Response(config_data)
