from rest_framework import viewsets, mixins

from story.models import Story
from story.serializers import StorySerializer


class StoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
