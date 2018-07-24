from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from popup.models import Popup
from popup.serializers import PopupSerializer


class PopupViewSet(ViewSet):
    def list(self, request):
        page = self.request.query_params.get('page', None)
        if page is not None:
            queryset = Popup.objects.filter(page=page)
        else:
            queryset = Popup.objects.all()

        serializer = PopupSerializer(queryset, many=True)
        return Response(serializer.data)
