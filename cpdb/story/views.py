from rest_framework import viewsets
from rest_framework.response import Response

from story.models import StoryPage
from story.serializers import StorySerializer


class StoryViewSet(viewsets.GenericViewSet):
    queryset = StoryPage.objects.all()
    serializer_class = StorySerializer

    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):  # pragma: no cover
        pass

    def get_serializer_context(self):
        return {
            'request': self.request,
            'view': self
        }
