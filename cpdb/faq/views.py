from rest_framework import viewsets

from faq.models import FAQPage
from faq.serializers import FAQSerializer


class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQPage.objects.all()
    serializer_class = FAQSerializer
