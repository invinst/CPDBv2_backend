from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from app_config.models import AppConfig


class AppConfigViewSet(ViewSet):
    def list(self, request):
        app_config = AppConfig.objects.all()
        config_data = {}
        for config_object in app_config:
            config_data[config_object.name] = config_object.value
        return Response(config_data)
