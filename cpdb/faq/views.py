from rest_framework import viewsets, mixins

from faq.models import FAQPage
from faq.serializers import FAQSerializer


class FAQViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = FAQPage.objects.all()
    serializer_class = FAQSerializer
