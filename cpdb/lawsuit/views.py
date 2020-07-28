from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from lawsuit.models import Lawsuit
from lawsuit.serializers import LawsuitSerializer


class LawsuitViewSet(ViewSet):
    def retrieve(self, _, pk):
        queryset = Lawsuit.objects.all()
        lawsuit = get_object_or_404(queryset, case_no=pk)
        return Response(LawsuitSerializer(lawsuit).data)
