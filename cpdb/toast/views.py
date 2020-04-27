from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from toast.constants import TOAST_DESKTOP_TEMPLATE_NAMES, TOAST_MOBILE_TEMPLATE_NAMES
from toast.models import Toast
from toast.serializers import ToastDesktopSerializer, ToastMobileSerializer


class ToastBaseViewSet(ViewSet):
    serializer = None

    def get_queryset(self):
        raise NotImplementedError

    def list(self, request):
        serializer = self.serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class ToastDesktopViewSet(ToastBaseViewSet):
    serializer = ToastDesktopSerializer

    def get_queryset(self):
        return Toast.objects.filter(name__in=TOAST_DESKTOP_TEMPLATE_NAMES)


class ToastMobileViewSet(ToastBaseViewSet):
    serializer = ToastMobileSerializer

    def get_queryset(self):
        return Toast.objects.filter(name__in=TOAST_MOBILE_TEMPLATE_NAMES)
