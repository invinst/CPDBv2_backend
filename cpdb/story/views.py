from rest_framework import viewsets, mixins, filters

from story.models import StoryPage
from story.serializers import StorySerializer


class StoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = StoryPage.objects.all()
    serializer_class = StorySerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('is_featured',)
