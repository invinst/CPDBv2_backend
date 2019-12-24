from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from toast.models import Toast
from toast.serializers import ToastSerializer


class ToastViewSet(ViewSet):
    def list(self, request):
        queryset = Toast.objects.all()

        serializer = ToastSerializer(queryset, many=True)
        return Response(serializer.data)
