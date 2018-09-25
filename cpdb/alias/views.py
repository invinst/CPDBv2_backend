from elasticsearch import NotFoundError
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .serializers import AliasSerializer
from .constants import ALIAS_MAPPINGS
from .utils import set_aliases


class AliasViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def update(self, request, alias_type, pk):
        try:
            doc_type_class, model_class = ALIAS_MAPPINGS[alias_type]
        except KeyError:
            return Response({'message': 'Cannot find type "{}"'.format(alias_type)}, status=status.HTTP_404_NOT_FOUND)

        aliases = AliasSerializer(data=request.data)
        if not aliases.is_valid():
            return Response({'message': aliases.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_aliases = aliases.validated_data['aliases']
        try:
            set_aliases(doc_type_class, model_class, pk, validated_aliases)
        except (NotFoundError, model_class.DoesNotExist):
            return Response({
                'message': 'Cannot find any "{alias_type}" record with pk={pk}'.format(pk=pk, alias_type=alias_type)
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': 'Aliases successfully updated', 'aliases': validated_aliases})
