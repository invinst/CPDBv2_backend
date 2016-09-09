from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from faq.models import FAQPage
from faq.serializers import FAQPageSerializer
from faq.utils import get_faq_parent_node


class FAQViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin):
    queryset = FAQPage.objects.live()
    serializer_class = FAQPageSerializer

    def create(self, request, *args, **kwargs):
        parent_page = get_faq_parent_node()

        faq_page = FAQPage(
            title=request.data.get('title', ''),
            body=[],
            live=False
        )

        try:
            parent_page.add_child(instance=faq_page)
        except DjangoValidationError as exc:
            raise ValidationError(detail={k: exc.message_dict[k] for k in ('title',)})

        serializer = self.get_serializer(faq_page)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
