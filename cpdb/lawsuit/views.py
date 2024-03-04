import random

from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from lawsuit.models import Lawsuit
from lawsuit.serializers import LawsuitSerializer, TopLawsuitSerializer

NUMBER_OF_TOP_LAWSUITS = 100
NUMBER_OF_RANDOM_TOP_LAWSUITS = 40


class LawsuitViewSet(ViewSet):
    def retrieve(self, _, pk):
        queryset = Lawsuit.objects.prefetch_related('payments').all()
        lawsuit = get_object_or_404(queryset, case_no=pk)
        return Response(LawsuitSerializer(lawsuit).data)

    @action(detail=False, methods=['GET'], url_path='top-lawsuits', url_name='top-lawsuits')
    def top_lawsuit(self, _):
        lawsuits = list(Lawsuit.objects.order_by('-total_payments')[:NUMBER_OF_TOP_LAWSUITS])
        top_lawsuits = random.sample(lawsuits, NUMBER_OF_RANDOM_TOP_LAWSUITS)
        return Response(TopLawsuitSerializer(top_lawsuits, many=True).data, status=status.HTTP_200_OK)
