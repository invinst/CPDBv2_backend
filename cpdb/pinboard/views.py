from django.shortcuts import get_object_or_404

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from data.models import Allegation
from .models import Pinboard
from .serializers import PinboardSerializer, PinboardComplaintSerializer


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

    @detail_route(methods=['GET'], url_path='complaints')
    def complaints(self, request, pk):
        pinboard = get_object_or_404(Pinboard, id=pk)
        crids = set(pinboard.allegations.values_list('crid', flat=True))
        complaints = Allegation.objects.filter(crid__in=crids)
        serializer = PinboardComplaintSerializer(complaints, many=True)
        return Response(serializer.data)
