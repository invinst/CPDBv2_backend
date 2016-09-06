from rest_framework import status, viewsets, mixins
from rest_framework.response import Response

from faq.models import FAQ
from faq.serializers import FAQSerializer


class FAQViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer

    def create(self, request, *args, **kwargs):
        faq = FAQ.objects.create(
            title=request.data.get('title', ''),
            body=[]
        )

        serializer = self.get_serializer(faq)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
