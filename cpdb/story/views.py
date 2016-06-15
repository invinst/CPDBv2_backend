from rest_framework import viewsets, mixins

from story.models import StoryPage
from story.serializers import StorySerializer


class StoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = StoryPage.objects.live()
    serializer_class = StorySerializer
