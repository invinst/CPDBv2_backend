from rest_framework import viewsets

from story.models import StoryPage
from story.serializers import StorySerializer


class StoryViewSet(viewsets.ModelViewSet):
    queryset = StoryPage.objects.all()
    serializer_class = StorySerializer
