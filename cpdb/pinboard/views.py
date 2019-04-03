from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Pinboard
from .serializers import PinboardSerializer


class PinboardViewSet(
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    queryset = Pinboard.objects.all()
    serializer_class = PinboardSerializer
    permission_classes = (AllowAny,)

    def create(self, request):
        response = super().create(request)
        request.session['pinboard-id'] = response.data['id']
        return response

    def update(self, request, pk):
        if 'pinboard-id' in request.session and \
               str(request.session['pinboard-id']) == str(pk):
            return super().update(request, pk)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, pk):
        pinboard = self.get_object()
        serializer_class = self.get_serializer_class()
        return Response(serializer_class(pinboard).data)
