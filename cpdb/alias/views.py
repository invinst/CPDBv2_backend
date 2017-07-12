from elasticsearch import NotFoundError
from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .serializers import AliasSerializer
from .constants import INDEXER_MAPPINGS
from .utils import set_aliases


class AliasViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def update(self, request, alias_type, pk):
        try:
            indexer_class = INDEXER_MAPPINGS[alias_type]
        except KeyError:
            raise NotFound('Cannot find type "{}"'.format(alias_type))

        aliases = AliasSerializer(data=request.data)
        aliases.is_valid(raise_exception=True)

        validated_aliases = aliases.validated_data['aliases']
        try:
            set_aliases(indexer_class, pk, validated_aliases)
        except NotFoundError:
            raise NotFound(
                'Cannot find any "{alias_type}" record with pk={pk}'.format(
                    pk=pk,
                    alias_type=alias_type
                )
            )

        return Response({
            'aliases': validated_aliases
        })
