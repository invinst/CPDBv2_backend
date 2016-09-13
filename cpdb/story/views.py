from rest_framework import viewsets, mixins

from story.models import StoryPage
from story.serializers import StoryPageSerializer


class StoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = StoryPage.objects.all()
    serializer_class = StoryPageSerializer
